"""
Forms for events app.
"""

from django import forms

from .models import Event, EventItem, EventParticipation, Payment


class EventForm(forms.ModelForm):
    """Form for creating and updating events."""

    event_date = forms.DateField(
        label="Data do Evento",
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent flatpickr-date",
                "type": "text",
                "placeholder": "Selecione a data",
            }
        ),
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "event_type",
            "event_date",
            "location",
            "location_url",
            "budget",
            "individual_amount",
            "pix_key",
            "pix_holder_name",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: Dia das Mães, Festa Junina",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Descreva o evento, objetivo e informações importantes",
                }
            ),
            "event_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: Escola Municipal João da Silva",
                }
            ),
            "location_url": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "https://maps.google.com/...",
                }
            ),
            "budget": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "individual_amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Calculado automaticamente",
                    "step": "0.01",
                }
            ),
            "pix_key": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "CPF, e-mail, telefone ou chave aleatória",
                }
            ),
            "pix_holder_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Nome do titular da conta",
                }
            ),
        }


class EventItemForm(forms.ModelForm):
    """Form for creating and updating event items."""

    class Meta:
        model = EventItem
        fields = ["name", "description", "item_type", "quantity", "unit_price"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: Bolo, Decoração, Lembrancinhas",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 2,
                    "placeholder": "Descrição do item (opcional)",
                }
            ),
            "item_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "min": "1",
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
        }


class PaymentForm(forms.ModelForm):
    """Form for creating payments."""

    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "pdf"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    class Meta:
        model = Payment
        fields = ["amount", "receipt", "notes"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "receipt": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "accept": "image/*,.pdf,application/pdf",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 2,
                    "placeholder": "Observações (opcional)",
                }
            ),
        }

    def clean_receipt(self):
        """Validate that the receipt is an image or PDF and not too large."""
        receipt = self.cleaned_data.get("receipt")
        if receipt:
            # Check file extension
            ext = receipt.name.split(".")[-1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Formato não permitido. Use: {', '.join(self.ALLOWED_EXTENSIONS)}"
                )
            # Check file size
            if receipt.size > self.MAX_FILE_SIZE:
                raise forms.ValidationError(
                    "O arquivo é muito grande. Tamanho máximo: 10MB"
                )
        return receipt


class ParticipationForm(forms.ModelForm):
    """Form for confirming participation in an event (potluck or presence)."""

    class Meta:
        model = EventParticipation
        fields = ["contribution", "guests_count", "notes"]
        widgets = {
            "contribution": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: Pão de queijo, biscoitos, suco de uva",
                }
            ),
            "guests_count": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "min": "1",
                    "max": "20",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 2,
                    "placeholder": "Observações, restrições alimentares, etc.",
                }
            ),
        }

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

        # Set default values
        self.fields["guests_count"].required = False
        self.fields["contribution"].required = False

        # Adjust fields based on event type
        if event:
            if event.is_potluck_event:
                self.fields["contribution"].required = True
                self.fields["contribution"].label = "O que você vai levar? *"
            else:
                # For non-potluck events, hide contribution field
                self.fields["contribution"].widget = forms.HiddenInput()

            if event.is_presence_event:
                self.fields["guests_count"].label = "Quantas pessoas irão?"
                self.fields["guests_count"].required = False
            else:
                # For non-presence events, hide guests_count field
                self.fields["guests_count"].widget = forms.HiddenInput()
                self.fields["guests_count"].initial = 1


class DeclineParticipationForm(forms.Form):
    """Form for declining participation in an event."""

    notes = forms.CharField(
        label="Motivo (opcional)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "rows": 2,
                "placeholder": "Motivo da recusa (opcional)",
            }
        ),
    )
