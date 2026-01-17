"""
Account models for School Hub.
Includes custom User model and Guardian profile.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model using email as the unique identifier.
    """

    username = None  # type: ignore
    email = models.EmailField(
        "E-mail",
        unique=True,
    )
    first_name = models.CharField(
        "Nome",
        max_length=150,
    )
    last_name = models.CharField(
        "Sobrenome",
        max_length=150,
        blank=True,
    )
    phone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True,
    )
    is_active = models.BooleanField(
        "Ativo",
        default=True,
    )
    date_joined = models.DateTimeField(
        "Data de cadastro",
        auto_now_add=True,
    )

    objects = UserManager()  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def get_full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name


class Guardian(BaseModel):
    """
    Guardian (parent/responsible) profile linked to a User.
    A guardian can have multiple students and be part of multiple classes.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="guardian",
        verbose_name="Usuário",
    )
    cpf = models.CharField(
        "CPF",
        max_length=14,
        blank=True,
        help_text="Formato: 000.000.000-00",
    )
    pix_key = models.CharField(
        "Chave PIX",
        max_length=100,
        blank=True,
        help_text="Chave PIX para recebimentos",
    )
    pix_holder_name = models.CharField(
        "Nome do Titular PIX",
        max_length=100,
        blank=True,
        help_text="Nome que aparece ao receber PIX",
    )
    address = models.TextField(
        "Endereço",
        blank=True,
    )
    notes = models.TextField(
        "Observações",
        blank=True,
    )

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self) -> str:
        return str(self.user)

    @property
    def email(self) -> str:
        """Return the guardian's email."""
        return self.user.email

    @property
    def phone(self) -> str:
        """Return the guardian's phone."""
        return self.user.phone

    @property
    def full_name(self) -> str:
        """Return the guardian's full name."""
        return self.user.get_full_name()
