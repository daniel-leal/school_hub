"""
URL configuration for accounts app.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cadastro/", views.RegisterView.as_view(), name="register"),
    # Profile
    path("perfil/", views.ProfileView.as_view(), name="profile"),
    path("perfil/editar/", views.ProfileUpdateView.as_view(), name="profile_update"),
    # Password
    path(
        "senha/alterar/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/accounts/senha/alterada/",
        ),
        name="password_change",
    ),
    path(
        "senha/alterada/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    # API
    path("api/pix-info/", views.PixInfoView.as_view(), name="pix_info"),
]
