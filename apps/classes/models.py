"""
Models for school classes, students, and class membership.
"""

import secrets

from django.db import models
from django.utils import timezone

from apps.accounts.models import Guardian
from apps.core.models import BaseModel


class SchoolClass(BaseModel):
    """
    Represents a school class (turma).
    A class groups students and their guardians for event management.
    """

    name = models.CharField(
        "Nome da Turma",
        max_length=100,
        help_text="Ex: 3º Ano A, Maternal II",
    )
    school = models.CharField(
        "Escola",
        max_length=200,
        blank=True,
    )
    year = models.PositiveIntegerField(
        "Ano Letivo",
        default=timezone.now().year,
    )
    description = models.TextField(
        "Descrição",
        blank=True,
    )
    invite_code = models.CharField(
        "Código de Convite",
        max_length=20,
        unique=True,
        editable=False,
    )
    is_active = models.BooleanField(
        "Ativa",
        default=True,
    )

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["-year", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.year})"

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self._generate_invite_code()
        super().save(*args, **kwargs)

    def _generate_invite_code(self) -> str:
        """Generate a unique invite code."""
        while True:
            code = secrets.token_urlsafe(8)[:10].upper()
            if not SchoolClass.objects.filter(invite_code=code).exists():
                return code

    def regenerate_invite_code(self) -> str:
        """Regenerate the invite code."""
        self.invite_code = self._generate_invite_code()
        self.save(update_fields=["invite_code", "updated_at"])
        return self.invite_code

    @property
    def member_count(self) -> int:
        """Return the number of members in this class."""
        return self.members.count()

    @property
    def student_count(self) -> int:
        """Return the number of students in this class."""
        return self.students.count()

    @property
    def active_events_count(self) -> int:
        """Return the number of active events."""
        return self.events.filter(is_active=True).count()


class ClassMember(BaseModel):
    """
    Represents a guardian's membership in a class.
    A guardian can be a member of multiple classes.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        MEMBER = "member", "Membro"

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Turma",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="class_memberships",
        verbose_name="Responsável",
    )
    role = models.CharField(
        "Papel",
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(
        "Entrou em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Membro da Turma"
        verbose_name_plural = "Membros da Turma"
        unique_together = ["school_class", "guardian"]
        ordering = ["guardian__user__first_name"]

    def __str__(self) -> str:
        return f"{self.guardian} - {self.school_class}"

    @property
    def is_admin(self) -> bool:
        """Check if the member is an admin."""
        return self.role == self.Role.ADMIN


class Student(BaseModel):
    """
    Represents a student in a class.
    A student is linked to a guardian and belongs to a class.
    """

    name = models.CharField(
        "Nome do Aluno",
        max_length=200,
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="Turma",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="Responsável",
    )
    birth_date = models.DateField(
        "Data de Nascimento",
        null=True,
        blank=True,
    )
    notes = models.TextField(
        "Observações",
        blank=True,
        help_text="Alergias, restrições alimentares, etc.",
    )

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ClassInvitation(BaseModel):
    """
    Represents an invitation to join a class.
    Can be a generic invite link or sent to a specific email.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        ACCEPTED = "accepted", "Aceito"
        EXPIRED = "expired", "Expirado"
        CANCELLED = "cancelled", "Cancelado"

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="Turma",
    )
    invited_by = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
        verbose_name="Convidado por",
    )
    email = models.EmailField(
        "E-mail do Convidado",
        blank=True,
        help_text="Deixe em branco para convite genérico",
    )
    token = models.CharField(
        "Token",
        max_length=64,
        unique=True,
        editable=False,
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    expires_at = models.DateTimeField(
        "Expira em",
    )
    accepted_at = models.DateTimeField(
        "Aceito em",
        null=True,
        blank=True,
    )
    accepted_by = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invitations",
        verbose_name="Aceito por",
    )

    class Meta:
        verbose_name = "Convite"
        verbose_name_plural = "Convites"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.email:
            return f"Convite para {self.email} - {self.school_class}"
        return f"Convite genérico - {self.school_class}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the invitation is still valid."""
        return self.status == self.Status.PENDING and not self.is_expired

    def accept(self, guardian: Guardian) -> ClassMember:
        """Accept the invitation and add guardian to the class."""
        if not self.is_valid:
            raise ValueError("Este convite não é mais válido.")

        # Create membership
        member, created = ClassMember.objects.get_or_create(
            school_class=self.school_class,
            guardian=guardian,
            defaults={"role": ClassMember.Role.MEMBER},
        )

        # Update invitation status
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.accepted_by = guardian
        self.save(update_fields=["status", "accepted_at", "accepted_by", "updated_at"])

        return member
