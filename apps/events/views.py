"""
Views for events app.
"""

import base64
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.classes.models import SchoolClass
from apps.core.services.pix import PixService

from .forms import (
    DeclineParticipationForm,
    EventForm,
    EventItemForm,
    ParticipationForm,
    PaymentForm,
)
from .models import Event, EventItem, EventParticipation, Payment


class EventListView(LoginRequiredMixin, ListView):
    """List all events the user can see."""

    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        guardian = getattr(self.request.user, "guardian", None)
        if guardian:
            # Get events from classes the user is a member of
            class_ids = guardian.class_memberships.values_list("school_class_id", flat=True)
            return Event.objects.filter(
                school_class_id__in=class_ids,
                is_active=True,
            ).select_related("school_class", "created_by__user")
        return Event.objects.none()


class EventDetailView(LoginRequiredMixin, DetailView):
    """View event details."""

    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guardian = getattr(self.request.user, "guardian", None)

        # Check user permissions
        context["is_admin"] = False
        context["has_paid"] = False
        context["my_payment"] = None
        context["my_participation"] = None
        context["has_confirmed_participation"] = False

        if guardian:
            membership = self.object.school_class.members.filter(guardian=guardian).first()
            context["is_admin"] = membership and membership.is_admin
            context["is_creator"] = self.object.created_by == guardian
            context["is_responsible"] = self.object.responsible == guardian
            context["can_edit"] = context["is_admin"] or context["is_creator"]
            # Can confirm payments: responsible, creator or admin
            context["can_confirm_payments"] = (
                context["is_admin"] or context["is_creator"] or context["is_responsible"]
            )

            # Check if user has paid
            my_payment = self.object.payments.filter(guardian=guardian).first()
            context["my_payment"] = my_payment
            context["has_paid"] = my_payment and my_payment.is_confirmed

            # Check participation status
            my_participation = self.object.participations.filter(guardian=guardian).first()
            context["my_participation"] = my_participation
            context["has_confirmed_participation"] = (
                my_participation and my_participation.is_confirmed
            )

        # Event items
        context["items"] = self.object.items.select_related("assigned_to__user").order_by("name")
        context["expense_items"] = self.object.items.filter(item_type=EventItem.ItemType.EXPENSE)
        context["contribution_items"] = self.object.items.filter(
            item_type=EventItem.ItemType.CONTRIBUTION
        )

        # Payments
        context["payments"] = self.object.payments.select_related("guardian__user").order_by(
            "-created_at"
        )
        context["confirmed_payments"] = self.object.payments.filter(status=Payment.Status.CONFIRMED)
        context["pending_payments"] = self.object.payments.filter(status=Payment.Status.PENDING)

        # Participations (for potluck/presence events)
        context["participations"] = self.object.participations.select_related(
            "guardian__user"
        ).order_by("-created_at")
        context["confirmed_participations"] = self.object.participations.filter(
            status=EventParticipation.Status.CONFIRMED
        )

        # Students status
        context["paid_students"] = self.object.paid_students
        context["pending_students"] = self.object.pending_students
        context["pending_participations_students"] = self.object.pending_participations_students

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """Create a new event."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_class"] = get_object_or_404(SchoolClass, pk=self.kwargs["class_id"])
        return context

    def form_valid(self, form):
        guardian = getattr(self.request.user, "guardian", None)
        school_class = get_object_or_404(SchoolClass, pk=self.kwargs["class_id"])

        self.object = form.save(commit=False)
        self.object.school_class = school_class
        self.object.created_by = guardian
        # Creator is responsible for confirming payments
        self.object.responsible = guardian

        # Calculate individual amount if budget is set
        if self.object.budget and not self.object.individual_amount:
            self.object.individual_amount = self.object.calculate_individual_amount()

        self.object.save()

        messages.success(self.request, f'Evento "{self.object.title}" criado com sucesso!')
        return redirect("events:detail", pk=self.object.pk)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """Update event details."""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Recalculate individual amount if budget changed
        if form.cleaned_data.get("budget") and not form.cleaned_data.get("individual_amount"):
            self.object.individual_amount = self.object.calculate_individual_amount()

        messages.success(self.request, "Evento atualizado com sucesso!")
        return super().form_valid(form)


class EventCloseView(LoginRequiredMixin, View):
    """Close an event."""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.close()
        messages.success(request, f'Evento "{event.title}" encerrado.')
        return redirect("events:detail", pk=pk)


class EventItemCreateView(LoginRequiredMixin, CreateView):
    """Add an item to an event."""

    model = EventItem
    form_class = EventItemForm
    template_name = "events/event_item_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = get_object_or_404(Event, pk=self.kwargs["event_id"])
        return context

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs["event_id"])
        self.object = form.save(commit=False)
        self.object.event = event
        self.object.save()

        messages.success(self.request, f'Item "{self.object.name}" adicionado!')
        return redirect("events:detail", pk=event.pk)


class EventItemUpdateView(LoginRequiredMixin, UpdateView):
    """Update event item."""

    model = EventItem
    form_class = EventItemForm
    template_name = "events/event_item_form.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.object.event.pk})

    def form_valid(self, form):
        messages.success(self.request, "Item atualizado com sucesso!")
        return super().form_valid(form)


class EventItemAssignView(LoginRequiredMixin, View):
    """Assign an item to the current user."""

    def post(self, request, pk):
        item = get_object_or_404(EventItem, pk=pk)
        guardian = getattr(request.user, "guardian", None)

        item.assigned_to = guardian
        item.save(update_fields=["assigned_to", "updated_at"])

        messages.success(request, f'Você assumiu o item "{item.name}".')
        return redirect("events:detail", pk=item.event.pk)


class EventItemCompleteView(LoginRequiredMixin, View):
    """Mark an item as completed."""

    def post(self, request, pk):
        item = get_object_or_404(EventItem, pk=pk)
        item.is_completed = True
        item.save(update_fields=["is_completed", "updated_at"])

        messages.success(request, f'Item "{item.name}" marcado como concluído.')
        return redirect("events:detail", pk=item.event.pk)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Create a payment for an event."""

    model = Payment
    form_class = PaymentForm
    template_name = "events/payment_form.html"

    def dispatch(self, request, *args, **kwargs):
        """Check if guardian has students in the event's class before allowing payment."""
        self.event = get_object_or_404(Event, pk=kwargs["event_id"])
        guardian = getattr(request.user, "guardian", None)

        if guardian:
            # Check if guardian has students in the event's class
            has_students = self.event.school_class.students.filter(guardian=guardian).exists()

            if not has_students:
                messages.error(
                    request,
                    "Você precisa ter pelo menos um aluno vinculado a esta turma para realizar pagamentos.",
                )
                return redirect("events:detail", pk=self.event.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        return context

    def get_initial(self):
        initial = super().get_initial()
        if self.event.individual_amount:
            initial["amount"] = self.event.individual_amount
        return initial

    def form_valid(self, form):
        guardian = getattr(self.request.user, "guardian", None)

        # Check if already paid
        existing = Payment.objects.filter(event=self.event, guardian=guardian).first()
        if existing:
            messages.warning(
                self.request,
                "Você já enviou um pagamento para este evento.",
            )
            return redirect("events:detail", pk=self.event.pk)

        self.object = form.save(commit=False)
        self.object.event = self.event
        self.object.guardian = guardian
        self.object.save()

        messages.success(
            self.request,
            "Comprovante enviado! Aguarde a confirmação do responsável.",
        )
        return redirect("events:detail", pk=self.event.pk)


class PaymentConfirmView(LoginRequiredMixin, View):
    """Confirm a payment."""

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        guardian = getattr(request.user, "guardian", None)
        event = payment.event

        # Check if user can confirm payments (responsible or admin)
        is_responsible = event.responsible == guardian or event.created_by == guardian
        membership = event.school_class.members.filter(guardian=guardian).first()
        is_admin = membership and membership.is_admin

        if not (is_responsible or is_admin):
            messages.error(
                request, "Você não tem permissão para confirmar pagamentos neste evento."
            )
            return redirect("events:detail", pk=event.pk)

        payment.confirm(guardian)
        messages.success(request, "Pagamento confirmado!")
        return redirect("events:detail", pk=event.pk)


class PaymentRejectView(LoginRequiredMixin, View):
    """Reject a payment."""

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        guardian = getattr(request.user, "guardian", None)
        event = payment.event

        # Check if user can reject payments (responsible or admin)
        is_responsible = event.responsible == guardian or event.created_by == guardian
        membership = event.school_class.members.filter(guardian=guardian).first()
        is_admin = membership and membership.is_admin

        if not (is_responsible or is_admin):
            messages.error(request, "Você não tem permissão para rejeitar pagamentos neste evento.")
            return redirect("events:detail", pk=event.pk)

        payment.reject()
        messages.warning(request, "Pagamento rejeitado.")
        return redirect("events:detail", pk=event.pk)


class EventPixView(LoginRequiredMixin, DetailView):
    """View PIX information and QR code for an event."""

    model = Event
    template_name = "events/event_pix.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate PIX code if key is available
        if self.object.pix_key:
            pix_service = PixService(
                pix_key=self.object.pix_key,
                merchant_name=self.object.pix_holder_name or "SCHOOL HUB",
                merchant_city="SAO PAULO",
            )

            amount = self.object.individual_amount or Decimal("0.00")
            # Use UUID hex (without hyphens) for transaction_id
            txid = self.object.id.hex[:25]

            context["pix_code"] = pix_service.generate_pix_code(
                amount=amount,
                description=self.object.title[:25],
                transaction_id=txid,
            )

            # Generate QR code as base64
            qr_bytes = pix_service.generate_qr_code(
                amount=amount,
                description=self.object.title[:25],
                transaction_id=txid,
            )
            context["qr_code_base64"] = base64.b64encode(qr_bytes).decode("utf-8")

        return context


class EventQRCodeView(LoginRequiredMixin, View):
    """Generate and return QR code image for PIX payment."""

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if not event.pix_key:
            return JsonResponse({"error": "PIX key not configured"}, status=400)

        pix_service = PixService(
            pix_key=event.pix_key,
            merchant_name=event.pix_holder_name or "SCHOOL HUB",
            merchant_city="SAO PAULO",
        )

        amount = event.individual_amount or Decimal("0.00")
        # Use UUID hex (without hyphens) for transaction_id
        txid = event.id.hex[:25]

        qr_bytes = pix_service.generate_qr_code(
            amount=amount,
            description=event.title[:25],
            transaction_id=txid,
        )

        return HttpResponse(qr_bytes, content_type="image/png")


class ParticipationCreateView(LoginRequiredMixin, CreateView):
    """Confirm participation in an event (potluck or presence)."""

    model = EventParticipation
    form_class = ParticipationForm
    template_name = "events/participation_form.html"

    def dispatch(self, request, *args, **kwargs):
        """Check if guardian has students and event allows participation."""
        self.event = get_object_or_404(Event, pk=kwargs["event_id"])
        guardian = getattr(request.user, "guardian", None)

        if not self.event.requires_participation:
            messages.error(request, "Este evento não requer confirmação de participação.")
            return redirect("events:detail", pk=self.event.pk)

        if guardian:
            # Check if guardian has students in the event's class
            has_students = self.event.school_class.students.filter(guardian=guardian).exists()

            if not has_students:
                messages.error(
                    request,
                    "Você precisa ter pelo menos um aluno vinculado a esta turma.",
                )
                return redirect("events:detail", pk=self.event.pk)

            # Check if already confirmed
            existing = EventParticipation.objects.filter(
                event=self.event, guardian=guardian
            ).first()
            if existing and existing.is_confirmed:
                messages.info(request, "Você já confirmou participação neste evento.")
                return redirect("events:detail", pk=self.event.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.event
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        return context

    def form_valid(self, form):
        guardian = getattr(self.request.user, "guardian", None)

        # Get or create participation
        participation, created = EventParticipation.objects.get_or_create(
            event=self.event,
            guardian=guardian,
        )

        # Update with form data (ensure guests_count has a default value)
        guests_count = form.cleaned_data.get("guests_count")
        if not guests_count:
            guests_count = 1

        participation.confirm(
            contribution=form.cleaned_data.get("contribution") or "",
            guests_count=guests_count,
            notes=form.cleaned_data.get("notes") or "",
        )

        if self.event.is_potluck_event and participation.contribution:
            messages.success(
                self.request,
                f"Participação confirmada! Você vai levar: {participation.contribution}",
            )
        else:
            messages.success(self.request, "Presença confirmada!")

        return redirect("events:detail", pk=self.event.pk)


class ParticipationDeclineView(LoginRequiredMixin, View):
    """Decline participation in an event."""

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        form = DeclineParticipationForm()
        return self._render(request, event, form)

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        guardian = getattr(request.user, "guardian", None)
        form = DeclineParticipationForm(request.POST)

        if form.is_valid():
            participation, created = EventParticipation.objects.get_or_create(
                event=event,
                guardian=guardian,
            )
            participation.decline(notes=form.cleaned_data.get("notes", ""))
            messages.info(request, "Participação recusada.")
            return redirect("events:detail", pk=event.pk)

        return self._render(request, event, form)

    def _render(self, request, event, form):
        from django.shortcuts import render

        return render(
            request,
            "events/participation_decline.html",
            {"event": event, "form": form},
        )


class ParticipationCancelView(LoginRequiredMixin, View):
    """Cancel a confirmed participation in an event."""

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        guardian = getattr(request.user, "guardian", None)

        if not event.requires_participation:
            messages.error(request, "Este evento não requer confirmação de participação.")
            return redirect("events:detail", pk=event.pk)

        participation = EventParticipation.objects.filter(
            event=event, guardian=guardian
        ).first()

        if not participation:
            messages.error(request, "Você não tem participação registrada neste evento.")
            return redirect("events:detail", pk=event.pk)

        if participation.status != EventParticipation.Status.CONFIRMED:
            messages.warning(request, "Sua participação não está confirmada.")
            return redirect("events:detail", pk=event.pk)

        # Cancel the participation
        participation.decline(notes="Cancelado pelo usuário")
        messages.info(request, "Sua participação foi cancelada.")
        return redirect("events:detail", pk=event.pk)
