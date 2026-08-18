from rest_framework import generics
from rest_framework.views import APIView
from .models import RecruitmentProcess, Stage, Application, StageProgress
from .permissions import IsStaffOrReadOnly
from .serializers import RecruitmentProcessSerializer, StageSerializer, ApplicationSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

class RecruitmentProcessQueryMixin:
    #sobrescrevendo método
    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return RecruitmentProcess.objects.all()

        return RecruitmentProcess.objects.exclude(
            status=RecruitmentProcess.Status.DRAFT
        )

class StageMixin:
    def get_queryset(self):
        process_id = self.kwargs["process_id"]
        user = self.request.user

        queryset = Stage.objects.filter(
            recruitment_process_id=process_id
        )

        if user.is_authenticated and user.is_staff:
            return queryset

        return queryset.exclude(
            recruitment_process__status=
            RecruitmentProcess.Status.DRAFT
        )


class RecruitmentProcessListCreateView(RecruitmentProcessQueryMixin, generics.ListCreateAPIView):
    serializer_class = RecruitmentProcessSerializer
    permission_classes = [IsStaffOrReadOnly]

    #sobreescrevendo método
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RecruitmentProcessDetailView(RecruitmentProcessQueryMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecruitmentProcessSerializer
    permission_classes = [IsStaffOrReadOnly]

    #sobrescrevendo método
    def perform_destroy(self, instance):
        if (instance.status != RecruitmentProcess.Status.DRAFT):
            raise ValidationError(
                {
                    "detail": (
                        "Apenas processos seletivos em rascunho podem ser excluídos"
                    )
                }
            )
        
        instance.delete()



class StageListCreateView(StageMixin, generics.ListCreateAPIView):
    serializer_class = StageSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        process_id = self.kwargs["process_id"]

        process = get_object_or_404(
            RecruitmentProcess,
            pk=process_id
        )

        if process.status != RecruitmentProcess.Status.DRAFT:
            raise ValidationError(
                {
                    "detail":(
                        "Etapas só pode ser adicionadas enquanto o processo seletivo estiver em rascunho."
                    )
                }
            )

        serializer.save(recruitment_process=process)

    #sobrescrever método
    def get_serializer_context(self):
        context = super().get_serializer_context()

        process_id = self.kwargs["process_id"]

        process = get_object_or_404(
            RecruitmentProcess,
            pk=process_id
        )

        context["recruitment_process"] = process

        return context


class StageDetailView(StageMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StageSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_destroy(self, instance):
        if instance.recruitment_process.status != instance.recruitment_process.Status.DRAFT :
            raise ValidationError(
                {
                    "detail": (
                        "Etapas só podem ser excluídas enquanto o processo seletivo estiver em rascunho"
                    )
                }
            )
        
        instance.delete()



class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        
        process_id = self.kwargs["process_id"]

        process = get_object_or_404(
            RecruitmentProcess,
            pk=process_id,
        )

        candidate = self.request.user

        queryset = Application.objects.filter(
            recruitment_process_id= process_id,
            candidate=candidate,
        )

        application = queryset.first()

        if application is None:
            serializer.save(candidate=candidate, recruitment_process=process)

        else:
            if application.status == Application.Status.ACTIVE:
                raise ValidationError(
                    {
                        "detail": ("Você já está inscrito nesse processo")
                    }
                )
            
            else:
                application.status = Application.Status.ACTIVE
                application.canceled_at = None
                application.save()

                serializer.instance = application



    def get_serializer_context(self):
        context = super().get_serializer_context()

        process_id = self.kwargs["process_id"]

        process = get_object_or_404(
            RecruitmentProcess,
            pk=process_id,
        )
        context["recruitment_process"] = process
        return context
        

class ApplicationCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, process_id):
        candidate = request.user

        application = Application.objects.filter(
            recruitment_process_id=process_id,
            candidate=candidate,
        ).first()

        if application is None:
            raise ValidationError(
                {
                    "detail": (
                        "Você não pode cancelar uma inscrição em um processo no qual não está inscrito."
                    )
                }
            )

        if application.status == Application.Status.CANCELED:
            raise ValidationError(
                {
                    "detail": (
                        "Sua inscrição nesse processo já está cancelada."
                    )
                }
            )

        application.status = Application.Status.CANCELED
        application.canceled_at = timezone.now()
        application.save()

        serializer = ApplicationSerializer(application)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user
        )


class ProcessApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        process_id = self.kwargs["process_id"]

        return Application.objects.filter(
            recruitment_process_id=process_id
        )



class RecruitmentProcessStartView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, process_id):
        process = get_object_or_404(
            RecruitmentProcess,
            pk=process_id,
        )

        now = timezone.now()

        if process.status != RecruitmentProcess.Status.PUBLISHED:
            raise ValidationError(
                {
                    "detail": (
                        "O processo seletivo precisa estar publicado para ser iniciado."
                    )
                }
            )

        if now <= process.registration_end:
            raise ValidationError(
                {
                    "detail": (
                        "O processo seletivo só pode ser iniciado após o encerramento das inscrições."
                    )
                }
            )

        if process.started_at is not None:
            raise ValidationError(
                {
                    "detail": (
                        "Este processo seletivo já foi iniciado."
                    )
                }
            )

        first_stage = process.stages.order_by("order").first()

        if first_stage is None:
            raise ValidationError(
                {
                    "detail": (
                        "O processo seletivo não possui etapas configuradas."
                    )
                }
            )

        applications = Application.objects.filter(
            recruitment_process=process,
            status=Application.Status.ACTIVE,
        )

        with transaction.atomic():
            progresses = [
                StageProgress(
                    application=application,
                    stage=first_stage,
                )
                for application in applications
            ]

            StageProgress.objects.bulk_create(progresses)

            process.started_at = now
            process.save(
                update_fields=["started_at"])

        return Response(
            {
                "detail": "Processo seletivo iniciado com sucesso.",
                "candidates_started": len(progresses),
                "first_stage": first_stage.id,
            },
            status=status.HTTP_200_OK,
        )
