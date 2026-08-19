from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ..models import Application, Stage, StageProgress
from .base import RecruitmentAPITestCase


class ApplicationReadContractTests(RecruitmentAPITestCase):
    def create_application_with_progresses(self, candidate, process):
        application = Application.objects.create(
            candidate=candidate,
            recruitment_process=process,
        )
        first_stage = Stage.objects.create(
            recruitment_process=process,
            title="First stage",
            description="First stage description",
            order=10,
        )
        current_stage = Stage.objects.create(
            recruitment_process=process,
            title="Current stage",
            description="Current stage description",
            order=30,
        )
        current_progress = StageProgress.objects.create(
            application=application,
            stage=current_stage,
        )
        first_progress = StageProgress.objects.create(
            application=application,
            stage=first_stage,
            status=StageProgress.Status.APPROVED,
            decided_at=timezone.now(),
        )
        return application, first_progress, current_progress

    def test_my_applications_returns_process_history_and_current_progress(self):
        process = self.create_process()
        application, first_progress, current_progress = (
            self.create_application_with_progresses(self.candidate, process)
        )
        self.client.force_authenticate(self.candidate)

        response = self.client.get(reverse("my-applications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data["id"], application.pk)
        self.assertEqual(
            data["recruitment_process"]["id"],
            process.pk,
        )
        self.assertEqual(
            [progress["id"] for progress in data["stage_progresses"]],
            [first_progress.pk, current_progress.pk],
        )
        self.assertEqual(
            [progress["stage"]["order"] for progress in data["stage_progresses"]],
            [10, 30],
        )
        self.assertEqual(data["current_progress"]["id"], current_progress.pk)
        self.assertEqual(
            data["current_progress"]["stage"],
            {
                "id": current_progress.stage_id,
                "title": "Current stage",
                "order": 30,
            },
        )

    def test_my_applications_only_returns_authenticated_candidate_data(self):
        own_process = self.create_process()
        own_application, _, own_progress = self.create_application_with_progresses(
            self.candidate,
            own_process,
        )
        other_candidate = self.create_user("other-candidate@example.com")
        other_process = self.create_process()
        other_application, _, other_progress = (
            self.create_application_with_progresses(other_candidate, other_process)
        )
        self.client.force_authenticate(self.candidate)

        response = self.client.get(reverse("my-applications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [application["id"] for application in response.data],
            [own_application.pk],
        )
        self.assertEqual(
            response.data[0]["current_progress"]["id"],
            own_progress.pk,
        )
        self.assertNotEqual(response.data[0]["id"], other_application.pk)
        self.assertNotEqual(
            response.data[0]["current_progress"]["id"],
            other_progress.pk,
        )

    def test_my_applications_requires_authentication(self):
        response = self.client.get(reverse("my-applications"))

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_admin_process_applications_returns_candidate_and_progress(self):
        process = self.create_process()
        application, first_progress, current_progress = (
            self.create_application_with_progresses(self.candidate, process)
        )
        other_process = self.create_process()
        other_candidate = self.create_user("outside-process@example.com")
        other_application, _, _ = self.create_application_with_progresses(
            other_candidate,
            other_process,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.get(
            reverse("process-applications", args=[process.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data["id"], application.pk)
        self.assertNotEqual(data["id"], other_application.pk)
        self.assertEqual(
            data["candidate"],
            {
                "id": self.candidate.pk,
                "full_name": self.candidate.full_name,
                "email": self.candidate.email,
                "phone": self.candidate.phone,
                "course": self.candidate.course,
                "semester": self.candidate.semester,
                "linkedin": self.candidate.linkedin,
                "github": self.candidate.github,
                "profile_picture": None,
            },
        )
        self.assertEqual(
            [progress["id"] for progress in data["stage_progresses"]],
            [first_progress.pk, current_progress.pk],
        )
        self.assertEqual(data["current_progress"]["id"], current_progress.pk)

    def test_process_applications_requires_staff_user(self):
        process = self.create_process()
        self.client.force_authenticate(self.candidate)

        response = self.client.get(
            reverse("process-applications", args=[process.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_current_progress_is_null_when_application_has_finished(self):
        process = self.create_process()
        application = Application.objects.create(
            candidate=self.candidate,
            recruitment_process=process,
            status=Application.Status.APPROVED,
        )
        stage = Stage.objects.create(
            recruitment_process=process,
            title="Only stage",
            description="Only stage description",
            order=1,
        )
        StageProgress.objects.create(
            application=application,
            stage=stage,
            status=StageProgress.Status.APPROVED,
            decided_at=timezone.now(),
        )
        self.client.force_authenticate(self.candidate)

        response = self.client.get(reverse("my-applications"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data[0]["current_progress"])

    def test_admin_list_query_count_does_not_grow_per_application(self):
        process = self.create_process()
        self.create_application_with_progresses(self.candidate, process)
        self.client.force_authenticate(self.staff)
        url = reverse("process-applications", args=[process.pk])

        with CaptureQueriesContext(connection) as single_application_queries:
            first_response = self.client.get(url)

        second_candidate = self.create_user("second-candidate@example.com")
        second_application = Application.objects.create(
            candidate=second_candidate,
            recruitment_process=process,
        )
        for stage in process.stages.all():
            StageProgress.objects.create(
                application=second_application,
                stage=stage,
            )

        with CaptureQueriesContext(connection) as multiple_application_queries:
            second_response = self.client.get(url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(single_application_queries),
            len(multiple_application_queries),
        )
