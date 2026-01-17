"""
Admin configuration for events app.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Event, EventItem, EventParticipation, Payment


class EventItemInline(TabularInline):
    """Inline for event items."""

    model = EventItem
    extra = 0
    autocomplete_fields = ["assigned_to"]


class PaymentInline(TabularInline):
    """Inline for payments."""

    model = Payment
    extra = 0
    autocomplete_fields = ["guardian"]
    readonly_fields = ["confirmed_by", "confirmed_at"]


class ParticipationInline(TabularInline):
    """Inline for participations."""

    model = EventParticipation
    extra = 0
    autocomplete_fields = ["guardian"]
    readonly_fields = ["confirmed_at"]


@admin.register(Event)
class EventAdmin(ModelAdmin):
    """Admin configuration for Event model."""

    list_display = [
        "title",
        "school_class",
        "event_type",
        "event_date",
        "budget_display",
        "progress_display",
        "is_active",
    ]
    list_filter = ["event_type", "is_active", "school_class", "event_date"]
    search_fields = ["title", "description", "school_class__name"]
    autocomplete_fields = ["school_class", "created_by", "responsible"]
    date_hierarchy = "event_date"
    inlines = [EventItemInline, PaymentInline, ParticipationInline]

    fieldsets = (
        (
            "Informações do Evento",
            {"fields": ("title", "description", "school_class", "event_type", "event_date")},
        ),
        (
            "Localização",
            {"fields": ("location", "location_url")},
        ),
        (
            "Financeiro",
            {"fields": ("budget", "individual_amount", "pix_key", "pix_holder_name")},
        ),
        (
            "Responsáveis",
            {"fields": ("created_by", "responsible")},
        ),
        (
            "Status",
            {"fields": ("is_active", "closed_at")},
        ),
    )

    @admin.display(description="Orçamento")
    def budget_display(self, obj):
        if obj.budget:
            return f"R$ {obj.budget:,.2f}"
        return "-"

    @admin.display(description="Progresso")
    def progress_display(self, obj):
        if obj.budget:
            percentage = obj.payment_progress_percentage
            color = "green" if percentage >= 100 else "orange" if percentage >= 50 else "red"
            return format_html(
                '<span style="color: {};">{} / {} ({}%)</span>',
                color,
                f"R$ {obj.total_collected:,.2f}",
                f"R$ {obj.budget:,.2f}",
                percentage,
            )
        return "-"


@admin.register(EventItem)
class EventItemAdmin(ModelAdmin):
    """Admin configuration for EventItem model."""

    list_display = ["name", "event", "item_type", "quantity", "unit_price", "assigned_to", "is_completed"]
    list_filter = ["item_type", "is_completed", "event"]
    search_fields = ["name", "event__title"]
    autocomplete_fields = ["event", "assigned_to"]

    fieldsets = (
        (
            "Item",
            {"fields": ("event", "name", "description", "item_type")},
        ),
        (
            "Valores",
            {"fields": ("quantity", "unit_price")},
        ),
        (
            "Atribuição",
            {"fields": ("assigned_to", "is_completed")},
        ),
    )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    """Admin configuration for Payment model."""

    list_display = ["guardian", "event", "amount_display", "status", "receipt_link"]
    list_filter = ["status", "event", "event__school_class"]
    search_fields = ["guardian__user__first_name", "guardian__user__last_name", "event__title"]
    autocomplete_fields = ["event", "guardian"]
    readonly_fields = ["confirmed_by", "confirmed_at"]
    actions = ["confirm_payments", "reject_payments"]

    fieldsets = (
        (
            "Pagamento",
            {"fields": ("event", "guardian", "amount", "receipt", "notes")},
        ),
        (
            "Status",
            {"fields": ("status", "confirmed_by", "confirmed_at")},
        ),
    )

    @admin.display(description="Valor")
    def amount_display(self, obj):
        return f"R$ {obj.amount:,.2f}"

    @admin.display(description="Comprovante")
    def receipt_link(self, obj):
        if obj.receipt:
            return format_html('<a href="{}" target="_blank">Ver</a>', obj.receipt.url)
        return "-"

    @admin.action(description="Confirmar pagamentos selecionados")
    def confirm_payments(self, request, queryset):
        guardian = getattr(request.user, "guardian", None)
        for payment in queryset.filter(status=Payment.Status.PENDING):
            payment.confirm(guardian)
        self.message_user(request, f"{queryset.count()} pagamento(s) confirmado(s).")

    @admin.action(description="Rejeitar pagamentos selecionados")
    def reject_payments(self, request, queryset):
        queryset.filter(status=Payment.Status.PENDING).update(status=Payment.Status.REJECTED)
        self.message_user(request, f"{queryset.count()} pagamento(s) rejeitado(s).")


@admin.register(EventParticipation)
class EventParticipationAdmin(ModelAdmin):
    """Admin configuration for EventParticipation model."""

    list_display = ["guardian", "event", "status", "contribution_display", "guests_count", "confirmed_at"]
    list_filter = ["status", "event", "event__school_class"]
    search_fields = ["guardian__user__first_name", "guardian__user__last_name", "event__title", "contribution"]
    autocomplete_fields = ["event", "guardian"]
    readonly_fields = ["confirmed_at"]

    fieldsets = (
        (
            "Participação",
            {"fields": ("event", "guardian", "status")},
        ),
        (
            "Detalhes",
            {"fields": ("contribution", "guests_count", "notes")},
        ),
        (
            "Confirmação",
            {"fields": ("confirmed_at",)},
        ),
    )

    @admin.display(description="Contribuição")
    def contribution_display(self, obj):
        if obj.contribution:
            return obj.contribution[:50] + "..." if len(obj.contribution) > 50 else obj.contribution
        return "-"
