from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    username = None

    full_name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20)

    course = models.CharField(max_length=100)

    semester = models.PositiveSmallIntegerField()

    linkedin = models.URLField()

    github = models.URLField(blank=True)

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'full_name',
        'phone',
        'course',
        'semester',
        'linkedin',
    ]

    objects = UserManager()