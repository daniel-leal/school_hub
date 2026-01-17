"""
Models for school events, items, and payments.
"""

from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.accounts.models import Guardian
from apps.classes.models import SchoolClass, Student
from apps.core.models import BaseModel


class Event(BaseModel):
    """
    Represents a school event.
    Events can have items that require payment or just assignments.
    """

    class EventType(models.TextChoices):
        PAYMENT = "payment", "Arrecadação"
        POTLUCK = "potluck", "Lanche Partilhado"
        PRESENCE = "presence", "Confirmação de Presença"
        MIXED = "mixed", "Misto"

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Turma",
    )
    created_by = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events",
        verbose_name="Criado por",
    )
    title = models.CharField(
        "Título",
        max_length=200,
    )
    description = models.TextField(
        "Descrição",
        help_text="Descreva o evento, objetivo e outras informações importantes",
    )
    event_type = models.CharField(
        "Tipo do Evento",
        max_length=20,
        choices=EventType.choices,
        default=EventType.PAYMENT,
    )
    event_date = models.DateField(
        "Data do Evento",
    )
    location = models.CharField(
        "Local do Evento",
        max_length=300,
        blank=True,
        help_text="Endereço ou local onde o evento será realizado",
    )
    location_url = models.URLField(
        "Link do Local",
        blank=True,
        help_text="Link do Google Maps ou similar",
    )
    budget = models.DecimalField(
        "Orçamento Total",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor total esperado para arrecadação",
    )
    individual_amount = models.DecimalField(
        "Valor por Pessoa",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculado automaticamente se não informado",
    )
    pix_key = models.CharField(
        "Chave PIX",
        max_length=100,
        blank=True,
        help_text="Chave PIX para recebimento",
    )
    pix_holder_name = models.CharField(
        "Nome do Titular",
        max_length=100,
        blank=True,
    )
    responsible = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_events",
        verbose_name="Responsável pela Arrecadação",
    )
    is_active = models.BooleanField(
        "Ativo",
        default=True,
    )
    closed_at = models.DateTimeField(
        "Encerrado em",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-event_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.school_class.name}"

    @property
    def is_payment_event(self) -> bool:
        """Check if this event requires payments."""
        return self.event_type in [self.EventType.PAYMENT, self.EventType.MIXED]

    @property
    def is_potluck_event(self) -> bool:
        """Check if this event is a potluck."""
        return self.event_type in [self.EventType.POTLUCK, self.EventType.MIXED]

    @property
    def is_presence_event(self) -> bool:
        """Check if this event requires presence confirmation."""
        return self.event_type == self.EventType.PRESENCE

    @property
    def requires_participation(self) -> bool:
        """Check if this event requires participation confirmation (potluck or presence)."""
        return self.event_type in [
            self.EventType.POTLUCK,
            self.EventType.PRESENCE,
            self.EventType.MIXED,
        ]

    @property
    def confirmed_participations(self):
        """Get confirmed participations for this event."""
        return self.participations.filter(status=EventParticipation.Status.CONFIRMED)

    @property
    def pending_participations_students(self):
        """Get students who haven't confirmed participation."""
        confirmed_guardian_ids = self.participations.filter(
            status=EventParticipation.Status.CONFIRMED
        ).values_list("guardian_id", flat=True)

        return Student.objects.filter(school_class=self.school_class).exclude(
            guardian_id__in=confirmed_guardian_ids
        )

    @property
    def total_collected(self) -> Decimal:
        """Calculate total amount collected."""
        return self.payments.filter(status=Payment.Status.CONFIRMED).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def total_pending(self) -> Decimal:
        """Calculate total amount pending."""
        if self.budget:
            return self.budget - self.total_collected
        return Decimal("0.00")

    @property
    def payment_progress_percentage(self) -> int:
        """Calculate payment progress as percentage."""
        if self.budget and self.budget > 0:
            return min(100, int((self.total_collected / self.budget) * 100))
        return 0

    @property
    def paid_students(self):
        """Get list of students who have paid."""
        return Student.objects.filter(
            guardian__payments__event=self,
            guardian__payments__status=Payment.Status.CONFIRMED,
        ).distinct()

    @property
    def pending_students(self):
        """Get list of students who haven't paid."""
        paid_guardian_ids = self.payments.filter(status=Payment.Status.CONFIRMED).values_list(
            "guardian_id", flat=True
        )

        return Student.objects.filter(school_class=self.school_class).exclude(
            guardian_id__in=paid_guardian_ids
        )

    def calculate_individual_amount(self) -> Decimal | None:
        """Calculate amount per person based on budget and student count."""
        if self.budget and self.school_class.student_count > 0:
            return (self.budget / self.school_class.student_count).quantize(Decimal("0.01"))
        return None

    def close(self):
        """Close the event."""
        self.is_active = False
        self.closed_at = timezone.now()
        self.save(update_fields=["is_active", "closed_at", "updated_at"])


class EventItem(BaseModel):
    """
    Represents an item in an event.
    Can be a payment item or a potluck item (what each person brings).
    """

    class ItemType(models.TextChoices):
        EXPENSE = "expense", "Despesa"
        CONTRIBUTION = "contribution", "Contribuição"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Evento",
    )
    name = models.CharField(
        "Nome do Item",
        max_length=200,
    )
    description = models.TextField(
        "Descrição",
        blank=True,
    )
    item_type = models.CharField(
        "Tipo",
        max_length=20,
        choices=ItemType.choices,
        default=ItemType.CONTRIBUTION,
    )
    quantity = models.PositiveIntegerField(
        "Quantidade",
        default=1,
    )
    unit_price = models.DecimalField(
        "Valor Unitário",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_items",
        verbose_name="Responsável",
    )
    is_completed = models.BooleanField(
        "Concluído",
        default=False,
    )

    class Meta:
        verbose_name = "Item do Evento"
        verbose_name_plural = "Itens do Evento"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.event.title}"

    @property
    def total_price(self) -> Decimal | None:
        """Calculate total price for this item."""
        if self.unit_price:
            return self.unit_price * self.quantity
        return None


class Payment(BaseModel):
    """
    Represents a payment made by a guardian for an event.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        CONFIRMED = "confirmed", "Confirmado"
        REJECTED = "rejected", "Rejeitado"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Evento",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Responsável",
    )
    amount = models.DecimalField(
        "Valor",
        max_digits=10,
        decimal_places=2,
    )
    receipt = models.FileField(
        "Comprovante",
        upload_to="receipts/%Y/%m/",
        blank=True,
        help_text="Aceita imagens (JPG, PNG) ou PDF",
    )
    notes = models.TextField(
        "Observações",
        blank=True,
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    confirmed_by = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_payments",
        verbose_name="Confirmado por",
    )
    confirmed_at = models.DateTimeField(
        "Confirmado em",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.guardian} - {self.event.title} - R$ {self.amount}"

    def confirm(self, confirmed_by: Guardian):
        """Confirm the payment."""
        self.status = self.Status.CONFIRMED
        self.confirmed_by = confirmed_by
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_by", "confirmed_at", "updated_at"])

    def reject(self):
        """Reject the payment."""
        self.status = self.Status.REJECTED
        self.save(update_fields=["status", "updated_at"])

    @property
    def is_confirmed(self) -> bool:
        """Check if payment is confirmed."""
        return self.status == self.Status.CONFIRMED


class EventParticipation(BaseModel):
    """
    Represents a participation confirmation for an event.
    Used for potluck events (what each person brings) and presence confirmation.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        CONFIRMED = "confirmed", "Confirmado"
        DECLINED = "declined", "Recusado"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name="Evento",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="event_participations",
        verbose_name="Responsável",
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    # For potluck events - what the person will bring
    contribution = models.CharField(
        "O que vai levar",
        max_length=300,
        blank=True,
        help_text="Ex: Pão de queijo, biscoitos, suco de uva",
    )
    # Number of people attending (for presence events)
    guests_count = models.PositiveIntegerField(
        "Quantidade de pessoas",
        default=1,
        help_text="Quantas pessoas irão ao evento",
    )
    notes = models.TextField(
        "Observações",
        blank=True,
        help_text="Informações adicionais, restrições alimentares, etc.",
    )
    confirmed_at = models.DateTimeField(
        "Confirmado em",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Participação"
        verbose_name_plural = "Participações"
        unique_together = ["event", "guardian"]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.guardian} - {self.event.title}"

    def confirm(self, contribution: str = "", guests_count: int = 1, notes: str = ""):
        """Confirm participation in the event."""
        self.status = self.Status.CONFIRMED
        self.contribution = contribution
        self.guests_count = guests_count
        self.notes = notes
        self.confirmed_at = timezone.now()
        self.save()

    def decline(self, notes: str = ""):
        """Decline participation in the event."""
        self.status = self.Status.DECLINED
        self.notes = notes
        self.save(update_fields=["status", "notes", "updated_at"])

    @property
    def is_confirmed(self) -> bool:
        """Check if participation is confirmed."""
        return self.status == self.Status.CONFIRMED
