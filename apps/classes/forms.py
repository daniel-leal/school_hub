"""
Forms for classes app.
"""

from django import forms

from .models import ClassInvitation, SchoolClass, Student


class ClassForm(forms.ModelForm):
    """Form for creating and updating classes."""

    class Meta:
        model = SchoolClass
        fields = ["name", "school", "year", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Ex: 3º Ano A",
                }
            ),
            "school": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Nome da escola",
                }
            ),
            "year": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Descrição da turma (opcional)",
                }
            ),
        }


class StudentForm(forms.ModelForm):
    """Form for creating and updating students."""

    class Meta:
        model = Student
        fields = ["name", "birth_date", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "Nome completo do aluno",
                }
            ),
            "birth_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "type": "date",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Observações importantes (alergias, restrições, etc.)",
                }
            ),
        }


class InvitationForm(forms.ModelForm):
    """Form for creating invitations."""

    class Meta:
        model = ClassInvitation
        fields = ["email", "expires_at"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "placeholder": "E-mail do convidado (opcional)",
                }
            ),
            "expires_at": forms.DateTimeInput(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                    "type": "datetime-local",
                }
            ),
        }


class JoinClassForm(forms.Form):
    """Form for joining a class with invite code."""

    invite_code = forms.CharField(
        label="Código de Convite",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent",
                "placeholder": "Digite o código de convite",
            }
        ),
    )
