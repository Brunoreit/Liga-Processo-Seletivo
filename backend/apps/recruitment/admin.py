from django.contrib import admin
from .models import RecruitmentProcess, Stage, Application

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