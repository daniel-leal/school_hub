"""
Forms for suppliers app.
"""

from django import forms

from .models import Supplier


class SupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers."""

    class Meta:
        model = Supplier
        fields = [
            "category",
            "name",
            "contact_name",
            "phone",
            "whatsapp",
            "email",
            "website",
            "instagram",
            "address",
            "maps_url",
            "description",
            "notes",
        ]
        widgets = {
            "category": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: Costureira, Decorador, Boleira, Buffet",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Nome do fornecedor ou empresa",
                }
            ),
            "contact_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Nome da pessoa de contato",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "whatsapp": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "email@exemplo.com",
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "https://www.site.com.br",
                }
            ),
            "instagram": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "usuario (sem @)",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 2,
                    "placeholder": "Endereço completo",
                }
            ),
            "maps_url": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "https://maps.google.com/...",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Serviços oferecidos, especialidades, etc.",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 2,
                    "placeholder": "Observações pessoais sobre o fornecedor",
                }
            ),
        }
