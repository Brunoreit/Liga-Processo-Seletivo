from django.contrib import admin
from .models import RecruitmentProcess

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
