from django.urls import path
from .views import RecruitmentProcessListCreateView, RecruitmentProcessDetailView, StageListCreateView, StageDetailView, ApplicationCreateView, ApplicationCancelView, MyApplicationsView, ProcessApplicationsView

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
        ApplicationCreateView.as_view(),
        name="application-create"
    ),

    path(
        "processes/<int:process_id>/applications/cancel/",
        ApplicationCancelView.as_view(),
        name="application-cancel",
    ),

    path(
        "applications/me/",
        MyApplicationsView.as_view(),
        name="my-applications",
    ),

    path(
        "processes/<int:process_id>/applications/list/",
        ProcessApplicationsView.as_view(),
        name="process-applications",
    ),
]