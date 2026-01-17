"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import Guardian, User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Admin configuration for User model."""

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ["email", "first_name", "last_name", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "phone")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Datas", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Guardian)
class GuardianAdmin(ModelAdmin):
    """Admin configuration for Guardian model."""

    list_display = ["user", "cpf", "pix_key"]
    list_filter = []
    search_fields = ["user__email", "user__first_name", "user__last_name", "cpf"]
    ordering = ["user__first_name", "user__last_name"]
    autocomplete_fields = ["user"]

    fieldsets = (
        (
            "Usuário",
            {"fields": ("user",)},
        ),
        (
            "Informações",
            {"fields": ("cpf", "pix_key", "address", "notes")},
        ),
    )
