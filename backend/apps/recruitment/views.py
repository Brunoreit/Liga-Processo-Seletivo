from rest_framework import generics
from .models import RecruitmentProcess
from .permissions import IsStaffOrReadOnly
from .serializers import RecruitmentProcessSerializer
from rest_framework.exceptions import ValidationError

class RecruitmentProcessQueryMixin:
    #sobrescrevendo método
    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return RecruitmentProcess.objects.all()

        return RecruitmentProcess.objects.exclude(
            status=RecruitmentProcess.Status.DRAFT
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