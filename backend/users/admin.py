from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        'email',
        'full_name',
        'course',
        'semester',
        'is_staff'
    )

    search_fields = (
        "email",
        "full_name",
    )

    ordering = (
        "full_name",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Informações pessoais",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "course",
                    "semester",
                    "linkedin",
                    "github",
                    "profile_picture",
                )
            },
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Datas importantes",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
)