from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        full_name,
        phone,
        course,
        semester,
        linkedin,
        **extra_fields,
    ):
        if not email:
            raise ValueError("O e-mail é obrigatório.")

        if not password:
            raise ValueError("A senha é obrigatória.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            full_name=full_name,
            phone=phone,
            course=course,
            semester=semester,
            linkedin=linkedin,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password,
        full_name,
        phone,
        course,
        semester,
        linkedin,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
    
        return self.create_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            course=course,
            semester=semester,
            linkedin=linkedin,
            **extra_fields,
    )