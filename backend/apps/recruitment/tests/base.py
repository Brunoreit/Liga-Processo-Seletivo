from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from ..models import RecruitmentProcess


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

