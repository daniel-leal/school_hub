"""
Admin configuration for suppliers app.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import Supplier, SupplierCategory


@admin.register(SupplierCategory)
class SupplierCategoryAdmin(ModelAdmin):
    """Admin configuration for SupplierCategory model."""

    list_display = ["name", "icon", "supplier_count"]
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {"fields": ("name", "description", "icon")},
        ),
    )

    @admin.display(description="Fornecedores")
    def supplier_count(self, obj):
        return obj.suppliers.count()


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    """Admin configuration for Supplier model."""

    list_display = [
        "name",
        "category",
        "phone",
        "whatsapp_link_display",
        "rating_display",
        "is_recommended",
        "is_active",
    ]
    list_filter = ["category", "is_recommended", "is_active", "rating"]
    search_fields = ["name", "contact_name", "phone", "email"]
    list_editable = ["is_recommended", "is_active"]

    fieldsets = (
        (
            "Informações Básicas",
            {"fields": ("name", "category", "contact_name", "description")},
        ),
        (
            "Contato",
            {"fields": ("phone", "whatsapp", "email", "website", "instagram")},
        ),
        (
            "Localização",
            {"fields": ("address", "latitude", "longitude")},
        ),
        (
            "Avaliação",
            {"fields": ("rating", "is_recommended", "notes")},
        ),
        (
            "Status",
            {"fields": ("is_active",)},
        ),
    )

    @admin.display(description="WhatsApp")
    def whatsapp_link_display(self, obj):
        if obj.whatsapp_link:
            return format_html(
                '<a href="{}" target="_blank" class="text-green-600">Abrir</a>',
                obj.whatsapp_link,
            )
        return "-"

    @admin.display(description="Avaliação")
    def rating_display(self, obj):
        if obj.rating:
            stars = "★" * obj.rating + "☆" * (5 - obj.rating)
            return format_html('<span class="text-yellow-500">{}</span>', stars)
        return "-"
