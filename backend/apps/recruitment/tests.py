from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Application, RecruitmentProcess, Stage, StageProgress


class RecruitmentAPITestCase(APITestCase):
    def create_user(self, email, *, is_staff=False):
        return get_user_model().objects.create_user(
            email=email,
            password="test-password",
            full_name="Test User",
            phone="19999999999",
            course="Computer Science",
            semester=1,
            linkedin="https://www.linkedin.com/in/test-user",
            is_staff=is_staff,
        )

    def create_process(self, *, registration_start=None, registration_end=None):
        now = timezone.now()
        return RecruitmentProcess.objects.create(
            title="Recruitment Process",
            description="Test process",
            status=RecruitmentProcess.Status.PUBLISHED,
            registration_start=registration_start or now - timedelta(days=1),
            registration_end=registration_end or now + timedelta(days=1),
            created_by=self.staff,
        )

    def setUp(self):
        self.staff = self.create_user("staff@example.com", is_staff=True)
        self.candidate = self.create_user("candidate@example.com")


class RecruitmentProcessValidationTests(RecruitmentAPITestCase):
    def test_process_cannot_be_created_as_published_or_closed(self):
        self.client.force_authenticate(self.staff)
        url = reverse("recruitment-process-list-create")
        now = timezone.now()

        for process_status in (
            RecruitmentProcess.Status.PUBLISHED,
            RecruitmentProcess.Status.CLOSED,
        ):
            with self.subTest(status=process_status):
                response = self.client.post(
                    url,
                    {
                        "title": "Recruitment Process",
                        "description": "Test process",
                        "status": process_status,
                        "registration_start": now,
                        "registration_end": now + timedelta(days=1),
                    },
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("status", response.data)

        self.assertFalse(RecruitmentProcess.objects.exists())

    def test_patch_registration_start_considers_saved_registration_end(self):
        process = self.create_process()
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            reverse("recruitment-process-detail", args=[process.pk]),
            {"registration_start": process.registration_end + timedelta(hours=1)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration_end", response.data)

    def test_patch_registration_end_considers_saved_registration_start(self):
        process = self.create_process()
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            reverse("recruitment-process-detail", args=[process.pk]),
            {"registration_end": process.registration_start - timedelta(hours=1)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("registration_end", response.data)


class ApplicationStatusTests(RecruitmentAPITestCase):
    def setUp(self):
        super().setUp()
        self.process = self.create_process()
        self.application_url = reverse("application-create", args=[self.process.pk])
        self.cancel_url = reverse("application-cancel", args=[self.process.pk])
        self.client.force_authenticate(self.candidate)

    def create_application(self, application_status):
        return Application.objects.create(
            candidate=self.candidate,
            recruitment_process=self.process,
            status=application_status,
            canceled_at=(
                timezone.now()
                if application_status == Application.Status.CANCELED
                else None
            ),
        )

    def test_active_application_cannot_be_reactivated(self):
        application = self.create_application(Application.Status.ACTIVE)

        response = self.client.post(self.application_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.ACTIVE)

    def test_canceled_application_can_be_reactivated(self):
        application = self.create_application(Application.Status.CANCELED)

        response = self.client.post(self.application_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.ACTIVE)
        self.assertIsNone(application.canceled_at)

    def test_approved_or_rejected_application_cannot_be_reactivated(self):
        for application_status in (
            Application.Status.APPROVED,
            Application.Status.REJECTED,
        ):
            with self.subTest(status=application_status):
                application = self.create_application(application_status)

                response = self.client.post(self.application_url, {}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                application.refresh_from_db()
                self.assertEqual(application.status, application_status)
                application.delete()

    def test_active_application_can_be_canceled(self):
        application = self.create_application(Application.Status.ACTIVE)

        response = self.client.post(self.cancel_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.CANCELED)
        self.assertIsNotNone(application.canceled_at)

    def test_approved_or_rejected_application_cannot_be_canceled(self):
        for application_status in (
            Application.Status.APPROVED,
            Application.Status.REJECTED,
        ):
            with self.subTest(status=application_status):
                application = self.create_application(application_status)

                response = self.client.post(self.cancel_url, {}, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                application.refresh_from_db()
                self.assertEqual(application.status, application_status)
                application.delete()


class RecruitmentProcessStartTests(RecruitmentAPITestCase):
    def create_startable_process(self):
        process = self.create_process(
            registration_start=timezone.now() - timedelta(days=2),
            registration_end=timezone.now() - timedelta(days=1),
        )
        Stage.objects.create(
            recruitment_process=process,
            title="First stage",
            description="First stage description",
            order=1,
        )
        return process

    def test_start_requires_staff_user(self):
        process = self.create_startable_process()
        self.client.force_authenticate(self.candidate)

        response = self.client.post(
            reverse("recruitment-process-start", args=[process.pk]),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        process.refresh_from_db()
        self.assertIsNone(process.started_at)

    def test_start_requires_registration_period_to_be_over(self):
        process = self.create_process(
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1),
        )
        Stage.objects.create(
            recruitment_process=process,
            title="First stage",
            description="First stage description",
            order=1,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("recruitment-process-start", args=[process.pk]),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        process.refresh_from_db()
        self.assertIsNone(process.started_at)

    def test_start_creates_progress_only_for_active_applications(self):
        process = self.create_startable_process()
        applications = {}

        for application_status in (
            Application.Status.ACTIVE,
            Application.Status.CANCELED,
            Application.Status.APPROVED,
            Application.Status.REJECTED,
        ):
            candidate = self.create_user(f"{application_status}@example.com")
            applications[application_status] = Application.objects.create(
                candidate=candidate,
                recruitment_process=process,
                status=application_status,
            )

        self.client.force_authenticate(self.staff)
        response = self.client.post(
            reverse("recruitment-process-start", args=[process.pk]),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["candidates_started"], 1)
        self.assertEqual(StageProgress.objects.count(), 1)
        self.assertTrue(
            StageProgress.objects.filter(
                application=applications[Application.Status.ACTIVE]
            ).exists()
        )

    def test_process_cannot_be_started_twice(self):
        process = self.create_startable_process()
        self.client.force_authenticate(self.staff)
        url = reverse("recruitment-process-start", args=[process.pk])

        first_response = self.client.post(url, {}, format="json")
        second_response = self.client.post(url, {}, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)


class StageProgressDecisionTests(RecruitmentAPITestCase):
    def setUp(self):
        super().setUp()
        self.process = self.create_process()
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
