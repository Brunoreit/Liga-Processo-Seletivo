from django.urls import path

from .views import CurrentUserView, RegisterUserView


urlpatterns = [
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

    path(
        "register/",
        RegisterUserView.as_view(),
        name="register-user"
    )
]