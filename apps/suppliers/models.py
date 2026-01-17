"""
Models for suppliers (vendors, service providers).
"""

from django.db import models

from apps.core.models import BaseModel


class SupplierCategory(BaseModel):
    """
    Category for suppliers (e.g., Costureira, Decoradora, Buffet).
    """

    name = models.CharField(
        "Nome",
        max_length=100,
    )
    description = models.TextField(
        "Descrição",
        blank=True,
    )
    icon = models.CharField(
        "Ícone",
        max_length=50,
        blank=True,
        help_text="Nome do ícone Material Design",
    )

    class Meta:
        verbose_name = "Categoria de Fornecedor"
        verbose_name_plural = "Categorias de Fornecedores"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(BaseModel):
    """
    Represents a supplier/vendor.
    Can be seamstresses, decorators, buffet services, etc.
    """

    category = models.CharField(
        "Categoria",
        max_length=100,
        blank=True,
        default="",
        help_text="Ex: Costureira, Decorador, Boleira, Buffet",
    )
    name = models.CharField(
        "Nome",
        max_length=200,
    )
    contact_name = models.CharField(
        "Nome do Contato",
        max_length=200,
        blank=True,
    )
    phone = models.CharField(
        "Telefone",
        max_length=20,
    )
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        blank=True,
    )
    email = models.EmailField(
        "E-mail",
        blank=True,
    )
    website = models.URLField(
        "Website",
        blank=True,
    )
    instagram = models.CharField(
        "Instagram",
        max_length=100,
        blank=True,
        help_text="Apenas o usuário, sem @",
    )
    address = models.TextField(
        "Endereço",
        blank=True,
    )
    maps_url = models.URLField(
        "Link do Google Maps",
        blank=True,
        help_text="Cole o link do Google Maps aqui",
    )
    description = models.TextField(
        "Descrição",
        blank=True,
        help_text="Serviços oferecidos, especialidades, etc.",
    )
    notes = models.TextField(
        "Observações",
        blank=True,
        help_text="Notas internas sobre o fornecedor",
    )
    rating = models.PositiveSmallIntegerField(
        "Avaliação",
        null=True,
        blank=True,
        help_text="Avaliação de 1 a 5 estrelas",
    )
    is_recommended = models.BooleanField(
        "Recomendado",
        default=False,
    )
    is_active = models.BooleanField(
        "Ativo",
        default=True,
    )

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def whatsapp_link(self) -> str:
        """Generate WhatsApp link."""
        phone = "".join(filter(str.isdigit, self.whatsapp or self.phone))
        if phone:
            return f"https://wa.me/55{phone}"
        return ""

    @property
    def instagram_link(self) -> str:
        """Generate Instagram link."""
        if self.instagram:
            username = self.instagram.lstrip("@")
            return f"https://instagram.com/{username}"
        return ""

    @property
    def maps_link(self) -> str:
        """Return Google Maps link."""
        if self.maps_url:
            return self.maps_url
        elif self.address:
            from urllib.parse import quote
            return f"https://www.google.com/maps/search/?api=1&query={quote(self.address)}"
        return ""
