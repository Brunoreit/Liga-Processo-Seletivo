from rest_framework import serializers
from apps.users.models import User
from .models import RecruitmentProcess, Stage, Application, StageProgress
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
            'started_at',
            'created_by',
        )

        read_only_fields = (
            'id',
            'published_at',
            'started_at',
            'created_by',
        )

    def validate(self, attrs):
        registration_start = attrs.get(
            "registration_start",
            self.instance.registration_start if self.instance else None,
        )
        registration_end = attrs.get(
            "registration_end",
            self.instance.registration_end if self.instance else None,
        )

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

        if (
            self.instance is None
            and attrs.get("status", RecruitmentProcess.Status.DRAFT)
            != RecruitmentProcess.Status.DRAFT
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "O processo seletivo deve ser criado como rascunho."
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

            if (
                current_status == RecruitmentProcess.Status.DRAFT
                and new_status == RecruitmentProcess.Status.PUBLISHED
                and not self.instance.stages.exists()
            ):
                raise serializers.ValidationError(
                    {
                        "status": (
                            "O processo seletivo precisa ter pelo menos uma etapa antes de ser publicado."
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



class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage

        fields = (
            'id',
            'recruitment_process',
            'title',
            'description',
            'order',
            'starts_at',
            'ends_at'
        )

        read_only_fields = (
            'id',
            'recruitment_process'
        )

    def validate(self, attrs):
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")

        if self.instance is not None:
            if "starts_at" not in attrs:
                starts_at = self.instance.starts_at

            if "ends_at" not in attrs:
                ends_at = self.instance.ends_at


        self._validate_dates(starts_at, ends_at)
        self._validate_process_dates(starts_at)
        self._validade_process_status(attrs)
        self._validate_stage_chronology(attrs,starts_at)
        self._validate_unique_order(attrs)
            
        return attrs



    def _validate_dates(self, starts_at, ends_at):
        if starts_at is None and ends_at is not None:
            raise serializers.ValidationError(
                {
                    "ends_at": (
                        "Fim da etapa não pode existir sem um início."
                    )
                }
            )

        if (
            starts_at is not None
            and ends_at is not None
            and ends_at <= starts_at
        ):
            raise serializers.ValidationError(
                {
                    "ends_at": (
                        "Fim da etapa deve ser posterior ao início."
                    )
                }
            )

        

    def _validade_process_status(self, attrs):
         if self.instance is None:
              return


         process_status = self.instance.recruitment_process.status

         if process_status == RecruitmentProcess.Status.CLOSED:
             raise serializers.ValidationError(
                 {
                     "detail":(
                         "Etapas de um processo seletivo encerrado não podem ser alteradas."
                     )
                 }
             )

         if (
             process_status == RecruitmentProcess.Status.PUBLISHED
             and "order" in attrs
             and attrs["order"] != self.instance.order
         ):
             raise serializers.ValidationError(
                 {
                     "order":(
                         "A ordem das etapas não pode ser alterada após a publicação."
                     )
                 }
             )

    def _validate_stage_chronology(self, attrs, starts_at):
        process = self._get_recruitment_process()

        order = attrs.get("order")

        if self.instance is not None and "order" not in attrs:
            order = self.instance.order

        if starts_at is None:
            return

        previous_stages = Stage.objects.filter(
                recruitment_process = process,
                order__lt = order,
                starts_at__isnull = False,
            )

        next_stages = Stage.objects.filter(
                recruitment_process=process,
                order__gt=order,
                starts_at__isnull=False,
            )

        if self.instance is not None:
            previous_stages = previous_stages.exclude(pk=self.instance.pk)
            next_stages = next_stages.exclude(pk=self.instance.pk)

        previous_stage = previous_stages.order_by("-order").first()
        next_stage = next_stages.order_by("order").first()
        
        if previous_stage is not None and starts_at < previous_stage.starts_at:
            raise serializers.ValidationError(
                {
                    "starts_at":("O início da etapa não pode ser anterior ao início de uma etapa anterior"
                    )
                }
            )

        if next_stage  is not None and starts_at > next_stage.starts_at:
            raise serializers.ValidationError(
                {
                    "starts_at": ("O início da etapa não pode ser posterior ao início de uma etapa seguinte."
                    )
                }
            )

    def _validate_process_dates(self, starts_at):
        process = self._get_recruitment_process()

        if starts_at is None or process is None:
            return

        if starts_at < process.registration_start:
            raise serializers.ValidationError(
                {
                    "starts_at": (
                        "A etapa não pode começar antes do início "
                        "das inscrições do processo seletivo."
                    )
                }
            )
        

    def _validate_unique_order(self, attrs):

        process = self._get_recruitment_process()

        order = attrs.get("order")

        if self.instance is not None and "order" not in attrs:
            order = self.instance.order

        if order is None or process is None:
            return

        stages = Stage.objects.filter(
            recruitment_process = process,
            order = order,
        )

        if self.instance is not None:
            stages = stages.exclude(pk=self.instance.pk)

        if stages.exists():
            raise serializers.ValidationError(
                {
                    "order": ("Já existe uma etapa com esta ordem neste processo seletivo.")
                }
            )

    # helper tano para casos de POST quanto de atualização
    def _get_recruitment_process(self):
        if self.instance is not None:
            return self.instance.recruitment_process

        return self.context.get("recruitment_process")


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application

        fields = (
            "id",
            "candidate",
            "recruitment_process",
            "status",
            "applied_at",
            "canceled_at",
        )

        read_only_fields = (
            "id",
            "candidate",
            "recruitment_process",
            "status",
            "applied_at",
            "canceled_at",
        )

    def validate(self, attrs):
        process = self._get_recruitment_process()
        now = timezone.now()

        if process.status != RecruitmentProcess.Status.PUBLISHED:
            raise serializers.ValidationError(
                {
                    "detail": ("Não é possível se inscrever nesse processo.")
                }
            )

        if now < process.registration_start:
            raise serializers.ValidationError(
                {
                    "detail":("As inscrições para esse processo ainda não começaram.")
                }
            )
        if now > process.registration_end:
            raise serializers.ValidationError(
                {
                    "detail": ("As inscrições para esse processo já foram encerradas.")
                }
            )
        return attrs

    def _get_recruitment_process(self):
        if self.instance is not None:
            return self.instance.recruitment_process
    
        return self.context.get("recruitment_process")


class StageProgressDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(
        choices=(
            StageProgress.Status.APPROVED,
            StageProgress.Status.REJECTED,
        )
    )


class StageSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = (
            "id",
            "title",
            "order",
        )
        read_only_fields = fields


class StageProgressReadSerializer(serializers.ModelSerializer):
    stage = StageSummarySerializer(read_only=True)

    class Meta:
        model = StageProgress
        fields = (
            "id",
            "status",
            "entered_at",
            "decided_at",
            "stage",
        )
        read_only_fields = fields


class RecruitmentProcessSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentProcess
        fields = (
            "id",
            "title",
            "status",
            "registration_start",
            "registration_end",
            "started_at",
        )
        read_only_fields = fields


class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "course",
            "semester",
            "linkedin",
            "github",
            "profile_picture",
        )
        read_only_fields = fields


def serialize_current_progress(application, context):
    progresses = getattr(application, "prefetched_stage_progresses", [])
    current_progress = next(
        (
            progress
            for progress in progresses
            if progress.status == StageProgress.Status.IN_REVIEW
        ),
        None,
    )

    if current_progress is None:
        return None

    return StageProgressReadSerializer(
        current_progress,
        context=context,
    ).data


class MyApplicationReadSerializer(serializers.ModelSerializer):
    recruitment_process = RecruitmentProcessSummarySerializer(read_only=True)
    stage_progresses = StageProgressReadSerializer(
        source="prefetched_stage_progresses",
        many=True,
        read_only=True,
    )
    current_progress = serializers.SerializerMethodField()

    def get_current_progress(self, application):
        return serialize_current_progress(application, self.context)

    class Meta:
        model = Application
        fields = (
            "id",
            "status",
            "applied_at",
            "canceled_at",
            "recruitment_process",
            "stage_progresses",
            "current_progress",
        )
        read_only_fields = fields


class AdminApplicationReadSerializer(serializers.ModelSerializer):
    candidate = CandidateSummarySerializer(read_only=True)
    stage_progresses = StageProgressReadSerializer(
        source="prefetched_stage_progresses",
        many=True,
        read_only=True,
    )
    current_progress = serializers.SerializerMethodField()

    def get_current_progress(self, application):
        return serialize_current_progress(application, self.context)

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate",
            "status",
            "applied_at",
            "canceled_at",
            "stage_progresses",
            "current_progress",
        )
        read_only_fields = fields
