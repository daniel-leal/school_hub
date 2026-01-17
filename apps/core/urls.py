"""
Core URL configuration.
Contains public-facing site URLs.
"""

from django.urls import path

from . import views

app_name = "site"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("sobre/", views.AboutView.as_view(), name="about"),
]
