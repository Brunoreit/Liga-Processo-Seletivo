from django.urls import path
from .views import RecruitmentProcessListCreateView, RecruitmentProcessDetailView

urlpatterns = [
    path(
        "processes/",
        RecruitmentProcessListCreateView.as_view(),
        name="recruitment-process-list-create"
    ),

    path(
        "processes/<int:pk>/",
        RecruitmentProcessDetailView.as_view(),
        name="recruitment-process-detail",
    )
]