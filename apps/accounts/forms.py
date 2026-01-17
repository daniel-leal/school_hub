"""
Forms for accounts app.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Guardian, User


class LoginForm(AuthenticationForm):
    """Custom login form."""

    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "seu@email.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "••••••••",
            }
        ),
    )


class RegisterForm(UserCreationForm):
    """User registration form."""

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "seu@email.com",
            }
        ),
    )
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "Seu nome",
            }
        ),
    )
    last_name = forms.CharField(
        label="Sobrenome",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "Seu sobrenome",
            }
        ),
    )
    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "(00) 00000-0000",
            }
        ),
    )
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "••••••••",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "••••••••",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "password1", "password2"]


class UserProfileForm(forms.ModelForm):
    """User profile update form."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
        }


class GuardianProfileForm(forms.ModelForm):
    """Guardian profile update form."""

    class Meta:
        model = Guardian
        fields = ["cpf", "pix_key", "pix_holder_name", "address", "notes"]
        widgets = {
            "cpf": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "000.000.000-00",
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
                    "placeholder": "Nome que aparece ao receber PIX",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                }
            ),
        }
