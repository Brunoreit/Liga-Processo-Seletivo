from django.contrib import admin
from .models import RecruitmentProcess, Stage, Application, StageProgress

class StageInLine(admin.TabularInline):
    model = Stage
    extra = 1

@admin.register(RecruitmentProcess)
class RecruitmentProcessAdmin(admin.ModelAdmin):
    model = RecruitmentProcess

    list_display = (
        'title',
        'status',
        'registration_start',
        'registration_end',
        'created_by'
    )

    list_filter = (
        'status',
        'created_by'
    )

    search_fields = (
        'title',
    )

    inlines = [StageInLine]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "candidate",
        "recruitment_process",
        "status",
        "applied_at",
        "canceled_at",
    )


    list_display_links = (
        "id",
        "candidate",
    ) 

    list_filter = (
        "status",
        "recruitment_process",
    )

    search_fields = (
        "candidate__email",
        "recruitment_process__title",
    )

@admin.register(StageProgress)
class StageProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "candidate",
        "recruitment_process",
        "stage",
        "stage_order",
        "status",
        "entered_at",
        "decided_at",
    )

    list_filter = (
        "status",
        "stage",
        "application__recruitment_process",
    )

    search_fields = (
        "application__candidate__email",
        "application__recruitment_process__title",
        "stage__title",
    )

    def candidate(self, obj):
        return obj.application.candidate

    def recruitment_process(self, obj):
        return obj.application.recruitment_process

    def stage_order(self, obj):
        return obj.stage.order