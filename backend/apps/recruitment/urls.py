from django.urls import path
from .views import RecruitmentProcessListCreateView, RecruitmentProcessDetailView, StageListCreateView, StageDetailView, ApplicationView

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
    ),

    path(
        "processes/<int:process_id>/stages/",
        StageListCreateView.as_view(),
        name="stage-list-create",
    ),

    path(
        "processes/<int:process_id>/stages/<int:pk>/",
        StageDetailView.as_view(),
        name="stage-detail",
    ),

    path(
        "processes/<int:process_id>/applications/",
        ApplicationView.as_view(),
        name="application-create"
    )
]