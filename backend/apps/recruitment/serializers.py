from rest_framework import serializers
from .models import RecruitmentProcess
from django.utils import timezone

class RecruitmentProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentProcess

        fields = (
            'id',
            'title',
            'description',
            'status',
            'registration_start',
            'registration_end',
            'published_at',
            'created_by',
        )

        read_only_fields = (
            'id',
            'published_at',
            'created_by'
        )

    def validate(self, attrs):
        registration_start = attrs.get("registration_start")
        registration_end = attrs.get("registration_end")

        if(
            registration_start is not None
            and registration_end is not None
            and registration_end <= registration_start
        ):
            raise serializers.ValidationError(
                {
                "registration_end": (
                    "O fim das inscrições deve ser posterior ao início"
                    )
                }
            )

        if self.instance is not None and "status" in attrs:
            current_status = self.instance.status
            new_status = attrs["status"]

            allowed_transitions = {
                RecruitmentProcess.Status.DRAFT: RecruitmentProcess.Status.PUBLISHED,
                RecruitmentProcess.Status.PUBLISHED: RecruitmentProcess.Status.CLOSED,
            }

            expected_next_status = allowed_transitions.get(current_status)

            if(
                new_status != current_status
                and new_status != expected_next_status
            ):
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Transição de status inválida"
                        )
                    }
                )

        return attrs

    # sobrescrever método
    def update(self, instance, validated_data):
        new_status = validated_data.get("status")

        if (instance.status == RecruitmentProcess.Status.DRAFT
        and new_status == RecruitmentProcess.Status.PUBLISHED
        ):
            validated_data["published_at"] = timezone.now()

        return super().update(instance, validated_data)

