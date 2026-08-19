from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ..models import Application
from .base import RecruitmentAPITestCase


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

    def test_application_cannot_be_canceled_after_process_start(self):
        application = self.create_application(Application.Status.ACTIVE)
        self.process.started_at = timezone.now()
        self.process.save(update_fields=["started_at"])

        response = self.client.post(self.cancel_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.ACTIVE)
        self.assertIsNone(application.canceled_at)
