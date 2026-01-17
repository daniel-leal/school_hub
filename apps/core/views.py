"""
Core views for public-facing pages.
"""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home page view."""

    template_name = "site/home.html"


class AboutView(TemplateView):
    """About page view."""

    template_name = "site/about.html"
