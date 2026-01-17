"""
URL configuration for suppliers app.
"""

from django.urls import path

from . import views

app_name = "suppliers"

urlpatterns = [
    path("", views.SupplierListView.as_view(), name="list"),
    path("novo/", views.SupplierCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.SupplierDetailView.as_view(), name="detail"),
    path("<uuid:pk>/editar/", views.SupplierUpdateView.as_view(), name="update"),
]
