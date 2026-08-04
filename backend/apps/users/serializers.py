from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "course",
            "semester",
            "linkedin",
            "github",
            "profile_picture",
        )
        read_only_fields = (
            "id",
            "email",
        )

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "password",
            "phone",
            "course",
            "semester",
            "linkedin",
            "github",
            "profile_picture"
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)