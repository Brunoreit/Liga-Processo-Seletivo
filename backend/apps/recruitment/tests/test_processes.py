from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ..models import Application, RecruitmentProcess, Stage, StageProgress
from .base import RecruitmentAPITestCase


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

