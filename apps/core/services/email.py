"""
Email service for sending transactional emails.
"""

import logging
from typing import TYPE_CHECKING, Protocol

from django.core.mail import EmailMultiAlternatives, send_mass_mail
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from apps.classes.models import ClassInvitation
    from apps.events.models import Event, Payment

logger = logging.getLogger(__name__)


class EmailServiceInterface(Protocol):
    def send_invitation_email(self, invitation: "ClassInvitation", invite_url: str) -> None: ...
    def send_payment_status_email(self, payment: "Payment") -> None: ...
    def send_event_notification_email(self, event: "Event") -> None: ...


class EmailService:
    """Sends transactional emails for School Hub."""

    def __init__(self, default_from_email: str) -> None:
        self.default_from_email = default_from_email

    def _send(self, subject: str, to: list[str], template: str, context: dict) -> None:
        """Render HTML + text templates and send. Logs on failure, never raises."""
        try:
            html = render_to_string(f"emails/{template}.html", context)
            text = render_to_string(f"emails/{template}.txt", context)
            msg = EmailMultiAlternatives(subject, text, self.default_from_email, to)
            msg.attach_alternative(html, "text/html")
            msg.send()
        except Exception:
            logger.exception("Failed to send email (template=%s, to=%s)", template, to)

    def send_invitation_email(self, invitation: "ClassInvitation", invite_url: str) -> None:
        if not invitation.email:
            return
        self._send(
            subject=f"Convite para a turma {invitation.school_class.name}",
            to=[invitation.email],
            template="invitation",
            context={"invitation": invitation, "invite_url": invite_url},
        )

    def send_payment_status_email(self, payment: "Payment") -> None:
        email = payment.guardian.user.email
        if not email:
            return
        self._send(
            subject=f"Atualização do pagamento — {payment.event.title}",
            to=[email],
            template="payment_status",
            context={"payment": payment},
        )

    def send_event_notification_email(self, event: "Event") -> None:
        members = event.school_class.members.select_related("guardian__user").all()
        recipients = [m.guardian.user.email for m in members if m.guardian and m.guardian.user.email]
        if not recipients:
            return
        try:
            text = render_to_string("emails/event_notification.txt", {"event": event})
            subject = f"Novo evento: {event.title}"
            datatuple = tuple((subject, text, self.default_from_email, [email]) for email in recipients)
            send_mass_mail(datatuple)
        except Exception:
            logger.exception("Failed to send event notification emails for event=%s", event.pk)
