"""
URL configuration for events app.
"""

from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    # Event list and detail
    path("", views.EventListView.as_view(), name="list"),
    path("novo/<uuid:class_id>/", views.EventCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.EventDetailView.as_view(), name="detail"),
    path("<uuid:pk>/editar/", views.EventUpdateView.as_view(), name="update"),
    path("<uuid:pk>/encerrar/", views.EventCloseView.as_view(), name="close"),
    # Event items
    path("<uuid:event_id>/itens/novo/", views.EventItemCreateView.as_view(), name="item_create"),
    path("itens/<uuid:pk>/editar/", views.EventItemUpdateView.as_view(), name="item_update"),
    path("itens/<uuid:pk>/assumir/", views.EventItemAssignView.as_view(), name="item_assign"),
    path("itens/<uuid:pk>/concluir/", views.EventItemCompleteView.as_view(), name="item_complete"),
    # Payments
    path("<uuid:event_id>/pagar/", views.PaymentCreateView.as_view(), name="payment_create"),
    path("pagamentos/<uuid:pk>/confirmar/", views.PaymentConfirmView.as_view(), name="payment_confirm"),
    path("pagamentos/<uuid:pk>/rejeitar/", views.PaymentRejectView.as_view(), name="payment_reject"),
    # Participation (potluck / presence confirmation)
    path("<uuid:event_id>/participar/", views.ParticipationCreateView.as_view(), name="participation_create"),
    path("<uuid:event_id>/recusar/", views.ParticipationDeclineView.as_view(), name="participation_decline"),
    path("<uuid:event_id>/cancelar-participacao/", views.ParticipationCancelView.as_view(), name="participation_cancel"),
    # PIX
    path("<uuid:pk>/pix/", views.EventPixView.as_view(), name="pix"),
    path("<uuid:pk>/qrcode/", views.EventQRCodeView.as_view(), name="qrcode"),
]
