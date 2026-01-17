"""
Dashboard views for School Hub.
"""

import json
from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView

from apps.classes.models import SchoolClass
from apps.events.models import Event, Payment


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view for guardians."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guardian = getattr(self.request.user, "guardian", None)

        if not guardian:
            context["has_guardian"] = False
            context["chart_labels"] = "[]"
            context["chart_data"] = "[]"
            return context

        context["has_guardian"] = True

        # Get user's classes
        class_ids = guardian.class_memberships.values_list("school_class_id", flat=True)
        classes = SchoolClass.objects.filter(id__in=class_ids, is_active=True)

        # Statistics
        context["total_classes"] = classes.count()
        context["total_students"] = guardian.students.count()

        # Events
        all_events = Event.objects.filter(school_class_id__in=class_ids)
        context["total_events"] = all_events.count()
        context["active_events"] = all_events.filter(is_active=True).count()

        # Upcoming events
        context["upcoming_events"] = all_events.filter(
            is_active=True,
            event_date__gte=date.today(),
        ).order_by("event_date")[:5]

        # My payments
        my_payments = Payment.objects.filter(guardian=guardian)
        context["total_payments"] = my_payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")
        context["pending_payments_count"] = my_payments.filter(
            status=Payment.Status.PENDING
        ).count()

        # Monthly expenses chart data
        monthly_data = list(
            my_payments.filter(status=Payment.Status.CONFIRMED)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )[:12]

        chart_labels = [item["month"].strftime("%b/%y") for item in monthly_data]
        chart_data = [float(item["total"]) for item in monthly_data]

        # Convert to JSON strings for safe JavaScript rendering
        context["chart_labels"] = json.dumps(chart_labels)
        context["chart_data"] = json.dumps(chart_data)

        # Recent payments
        context["recent_payments"] = my_payments.select_related(
            "event__school_class"
        ).order_by("-created_at")[:5]

        # Classes with their stats (use distinct=True to avoid incorrect counts due to JOINs)
        context["classes"] = classes.annotate(
            events_total=Count("events", distinct=True),
            students_total=Count("students", distinct=True),
        )

        return context


def dashboard_callback(request, context):
    """
    Callback for Unfold admin dashboard.
    Adds custom statistics and charts to the admin dashboard.
    """
    from django.db.models import Sum
    from django.db.models.functions import TruncMonth

    # Total statistics
    total_classes = SchoolClass.objects.filter(is_active=True).count()
    total_events = Event.objects.count()
    active_events = Event.objects.filter(is_active=True).count()
    total_payments = Payment.objects.filter(
        status=Payment.Status.CONFIRMED
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    # Monthly events chart
    monthly_events = (
        Event.objects.annotate(month=TruncMonth("event_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )[:12]

    # Monthly payments chart
    monthly_payments = (
        Payment.objects.filter(status=Payment.Status.CONFIRMED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )[:12]

    context.update(
        {
            "stats": {
                "total_classes": total_classes,
                "total_events": total_events,
                "active_events": active_events,
                "total_payments": f"R$ {total_payments:,.2f}",
            },
            "charts": {
                "events": {
                    "labels": [item["month"].strftime("%b/%y") for item in monthly_events],
                    "data": [item["count"] for item in monthly_events],
                },
                "payments": {
                    "labels": [item["month"].strftime("%b/%y") for item in monthly_payments],
                    "data": [float(item["total"]) for item in monthly_payments],
                },
            },
        }
    )

    return context
