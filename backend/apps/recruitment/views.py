from rest_framework import generics
from .models import RecruitmentProcess, Stage, Application
from .permissions import IsStaffOrReadOnly
from .serializers import RecruitmentProcessSerializer, StageSerializer, ApplicationSerializer
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

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

class ApplicationView(generics.CreateAPIView):
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
        


