from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ..models import RecruitmentProcess, Stage
from .base import RecruitmentAPITestCase


class StageLifecycleTests(RecruitmentAPITestCase):
    def create_draft_process(self, *, started=False):
        process = self.create_process()
        process.status = RecruitmentProcess.Status.DRAFT
        process.started_at = timezone.now() if started else None
        process.save(update_fields=["status", "started_at"])
        return process

    def test_stage_cannot_be_created_after_process_start(self):
        process = self.create_draft_process(started=True)
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("stage-list-create", args=[process.pk]),
            {
                "title": "New stage",
                "description": "New stage description",
                "order": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(process.stages.exists())

    def test_stage_cannot_be_updated_after_process_start(self):
        process = self.create_draft_process(started=True)
        stage = Stage.objects.create(
            recruitment_process=process,
            title="Original stage",
            description="Original description",
            order=1,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            reverse("stage-detail", args=[process.pk, stage.pk]),
            {"title": "Changed stage"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        stage.refresh_from_db()
        self.assertEqual(stage.title, "Original stage")

    def test_stage_cannot_be_deleted_after_process_start(self):
        process = self.create_draft_process(started=True)
        stage = Stage.objects.create(
            recruitment_process=process,
            title="Stage",
            description="Stage description",
            order=1,
        )
        self.client.force_authenticate(self.staff)

        response = self.client.delete(
            reverse("stage-detail", args=[process.pk, stage.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Stage.objects.filter(pk=stage.pk).exists())

    def test_stage_operations_remain_available_for_draft_process(self):
        process = self.create_draft_process()
        self.client.force_authenticate(self.staff)
        list_url = reverse("stage-list-create", args=[process.pk])

        create_response = self.client.post(
            list_url,
            {
                "title": "Stage",
                "description": "Stage description",
                "order": 1,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        stage = Stage.objects.get(pk=create_response.data["id"])

        update_response = self.client.patch(
            reverse("stage-detail", args=[process.pk, stage.pk]),
            {"title": "Updated stage"},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        stage.refresh_from_db()
        self.assertEqual(stage.title, "Updated stage")

        delete_response = self.client.delete(
            reverse("stage-detail", args=[process.pk, stage.pk])
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Stage.objects.filter(pk=stage.pk).exists())
