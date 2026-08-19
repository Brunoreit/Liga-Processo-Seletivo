from unittest.mock import patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ..models import Application, RecruitmentProcess, Stage, StageProgress
from .base import RecruitmentAPITestCase


class StageProgressDecisionTests(RecruitmentAPITestCase):
    def setUp(self):
        super().setUp()
        self.process = self.create_process()
        self.process.started_at = timezone.now()
        self.process.save(update_fields=["started_at"])
        self.application = Application.objects.create(
            candidate=self.candidate,
            recruitment_process=self.process,
        )
        self.first_stage = Stage.objects.create(
            recruitment_process=self.process,
            title="First stage",
            description="First stage description",
            order=10,
        )
        self.progress = StageProgress.objects.create(
            application=self.application,
            stage=self.first_stage,
        )
        self.url = reverse("stage-progress-decision", args=[self.progress.pk])

    def test_decision_requires_published_process(self):
        self.process.status = RecruitmentProcess.Status.DRAFT
        self.process.save(update_fields=["status"])
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)

    def test_decision_requires_started_process(self):
        self.process.started_at = None
        self.process.save(update_fields=["started_at"])
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)

    def test_decision_is_rejected_for_closed_process(self):
        self.process.status = RecruitmentProcess.Status.CLOSED
        self.process.save(update_fields=["status"])
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.progress.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)
        self.assertIsNone(self.progress.decided_at)
        self.assertEqual(self.application.status, Application.Status.ACTIVE)

    def test_model_clean_rejects_progress_from_different_process(self):
        other_process = self.create_process()
        other_stage = Stage.objects.create(
            recruitment_process=other_process,
            title="Other stage",
            description="Other stage description",
            order=1,
        )
        progress = StageProgress(
            application=self.application,
            stage=other_stage,
        )

        with self.assertRaises(DjangoValidationError):
            progress.clean()

    def test_staff_can_approve_and_advance_to_next_stage_with_order_gap(self):
        next_stage = Stage.objects.create(
            recruitment_process=self.process,
            title="Next stage",
            description="Next stage description",
            order=30,
        )
        Stage.objects.create(
            recruitment_process=self.process,
            title="Last stage",
            description="Last stage description",
            order=50,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.progress.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.APPROVED)
        self.assertIsNotNone(self.progress.decided_at)
        self.assertEqual(self.application.status, Application.Status.ACTIVE)
        next_progress = StageProgress.objects.get(
            application=self.application, stage=next_stage
        )
        self.assertEqual(next_progress.status, StageProgress.Status.IN_REVIEW)
        self.assertEqual(response.data["next_stage_id"], next_stage.pk)
        self.assertEqual(response.data["next_progress_id"], next_progress.pk)

    def test_approval_on_last_stage_approves_application(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.progress.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.APPROVED)
        self.assertIsNotNone(self.progress.decided_at)
        self.assertEqual(self.application.status, Application.Status.APPROVED)
        self.assertIsNone(response.data["next_stage_id"])
        self.assertEqual(StageProgress.objects.count(), 1)

    def test_rejection_rejects_progress_and_application(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "rejected"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.progress.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.REJECTED)
        self.assertIsNotNone(self.progress.decided_at)
        self.assertEqual(self.application.status, Application.Status.REJECTED)
        self.assertEqual(StageProgress.objects.count(), 1)

    def test_decision_requires_staff_user(self):
        self.client.force_authenticate(self.candidate)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)

    def test_decision_requires_authentication(self):
        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)

    def test_invalid_decision_is_rejected(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "pending"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("decision", response.data)

    def test_decision_is_required(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("decision", response.data)

    def test_nonexistent_progress_returns_not_found(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("stage-progress-decision", args=[999999]),
            {"decision": "approved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_progress_must_be_in_review(self):
        self.client.force_authenticate(self.staff)

        for progress_status in (
            StageProgress.Status.APPROVED,
            StageProgress.Status.REJECTED,
        ):
            with self.subTest(status=progress_status):
                self.progress.status = progress_status
                self.progress.decided_at = timezone.now()
                self.progress.save(update_fields=["status", "decided_at"])

                response = self.client.post(
                    self.url, {"decision": "rejected"}, format="json"
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.application.refresh_from_db()
                self.assertEqual(self.application.status, Application.Status.ACTIVE)

    def test_application_must_be_active(self):
        self.client.force_authenticate(self.staff)

        for application_status in (
            Application.Status.CANCELED,
            Application.Status.APPROVED,
            Application.Status.REJECTED,
        ):
            with self.subTest(status=application_status):
                self.application.status = application_status
                self.application.save(update_fields=["status"])

                response = self.client.post(
                    self.url, {"decision": "approved"}, format="json"
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.progress.refresh_from_db()
                self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)
                self.assertIsNone(self.progress.decided_at)

    def test_existing_progress_for_next_stage_prevents_decision(self):
        next_stage = Stage.objects.create(
            recruitment_process=self.process,
            title="Next stage",
            description="Next stage description",
            order=20,
        )
        StageProgress.objects.create(
            application=self.application,
            stage=next_stage,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)
        self.assertIsNone(self.progress.decided_at)

    def test_stage_and_application_must_belong_to_same_process(self):
        other_process = self.create_process()
        other_stage = Stage.objects.create(
            recruitment_process=other_process,
            title="Other stage",
            description="Other stage description",
            order=1,
        )
        self.progress.stage = other_stage
        self.progress.save(update_fields=["stage"])
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            self.url, {"decision": "approved"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)

    def test_operation_is_atomic_when_next_progress_creation_fails(self):
        Stage.objects.create(
            recruitment_process=self.process,
            title="Next stage",
            description="Next stage description",
            order=20,
        )
        self.client.force_authenticate(self.staff)

        with patch(
            "apps.recruitment.views.StageProgress.objects.create",
            side_effect=DatabaseError("forced failure"),
        ):
            with self.assertRaises(DatabaseError):
                self.client.post(
                    self.url, {"decision": "approved"}, format="json"
                )

        self.progress.refresh_from_db()
        self.application.refresh_from_db()
        self.assertEqual(self.progress.status, StageProgress.Status.IN_REVIEW)
        self.assertIsNone(self.progress.decided_at)
        self.assertEqual(self.application.status, Application.Status.ACTIVE)
        self.assertEqual(StageProgress.objects.count(), 1)
