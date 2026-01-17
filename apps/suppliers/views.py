"""
Views for suppliers app.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import SupplierForm
from .models import Supplier


class SupplierListView(LoginRequiredMixin, ListView):
    """List all active suppliers."""

    model = Supplier
    template_name = "suppliers/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 12

    def get_queryset(self):
        queryset = Supplier.objects.filter(is_active=True)

        # Filter by category if specified
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category__icontains=category)

        # Search
        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by("-is_recommended", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get distinct categories from existing suppliers
        context["categories"] = (
            Supplier.objects.filter(is_active=True)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )
        context["current_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class SupplierDetailView(LoginRequiredMixin, DetailView):
    """View supplier details."""

    model = Supplier
    template_name = "suppliers/supplier_detail.html"
    context_object_name = "supplier"


class SupplierCreateView(LoginRequiredMixin, CreateView):
    """Create a new supplier."""

    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"

    def get_success_url(self):
        return reverse_lazy("suppliers:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Fornecedor cadastrado com sucesso!")
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing supplier."""

    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"

    def get_success_url(self):
        return reverse_lazy("suppliers:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Fornecedor atualizado com sucesso!")
        return super().form_valid(form)
