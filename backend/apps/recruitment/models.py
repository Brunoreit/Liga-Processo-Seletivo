from django.conf import settings
from django.db import models


class RecruitmentProcess(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado"
        CLOSED = "closed", "Encerrado"

    title = models.CharField(max_length=150)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()

    published_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_recruitment_processes",
    )

    def __str__(self):
        return self.title

class Stage(models.Model):
    recruitment_process = models.ForeignKey(
        RecruitmentProcess,
        on_delete=models.CASCADE,
        related_name="stages",
    )

    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField()

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ends_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["recruitment_process", "order"],
                name="unique_stage_order_per_recruitment_process"
            )
        ]

    def __str__(self):
        return f"{self.order} - {self.title}"