"""
Views for accounts app.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.classes.models import ClassMember, SchoolClass

from .forms import GuardianProfileForm, LoginForm, RegisterForm, UserProfileForm
from .models import Guardian


class LoginView(auth_views.LoginView):
    """Custom login view."""

    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True


class RegisterView(CreateView):
    """User registration view."""

    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("dashboard:index")

    def get(self, request, *args, **kwargs):
        """Store class code in session if provided."""
        class_code = request.GET.get("class_code")
        if class_code:
            # Verify the class exists
            if SchoolClass.objects.filter(invite_code=class_code, is_active=True).exists():
                request.session["pending_class_code"] = class_code
            else:
                messages.warning(request, "Código de turma inválido ou turma não encontrada.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show pending class info if available
        class_code = self.request.session.get("pending_class_code")
        if class_code:
            school_class = SchoolClass.objects.filter(
                invite_code=class_code, is_active=True
            ).first()
            context["pending_class"] = school_class
        return context

    def form_valid(self, form):
        """Create user and guardian profile, then log in."""
        user = form.save()

        # Create guardian profile
        guardian = Guardian.objects.create(user=user)

        # Check if there's a pending class to join
        class_code = self.request.session.pop("pending_class_code", None)
        if class_code:
            school_class = SchoolClass.objects.filter(
                invite_code=class_code, is_active=True
            ).first()
            if school_class:
                ClassMember.objects.get_or_create(
                    school_class=school_class,
                    guardian=guardian,
                    defaults={"role": ClassMember.Role.MEMBER},
                )
                messages.success(
                    self.request,
                    f"Você foi adicionado à turma '{school_class.name}'!",
                )

        # Log in the user
        login(self.request, user)

        messages.success(
            self.request,
            f"Bem-vindo(a), {user.first_name}! Sua conta foi criada com sucesso.",
        )
        return redirect(str(self.success_url))


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["guardian"] = getattr(self.request.user, "guardian", None)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """User profile update view."""

    template_name = "accounts/profile_update.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guardian = getattr(self.request.user, "guardian", None)
        if guardian:
            if self.request.POST:
                context["guardian_form"] = GuardianProfileForm(self.request.POST, instance=guardian)
            else:
                context["guardian_form"] = GuardianProfileForm(instance=guardian)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Update guardian profile if exists
        guardian = getattr(self.request.user, "guardian", None)
        if guardian:
            guardian_form = GuardianProfileForm(self.request.POST, instance=guardian)
            if guardian_form.is_valid():
                guardian_form.save()

        messages.success(self.request, "Perfil atualizado com sucesso!")
        return response


class PixInfoView(LoginRequiredMixin, View):
    """API endpoint to get user's PIX information."""

    def get(self, request):
        guardian = getattr(request.user, "guardian", None)

        if not guardian:
            return JsonResponse({"error": "Perfil não encontrado"}, status=404)

        # Return PIX info, using user's name as default holder name
        pix_key = guardian.pix_key or ""
        pix_holder_name = guardian.pix_holder_name or request.user.get_full_name()

        return JsonResponse(
            {
                "pix_key": pix_key,
                "pix_holder_name": pix_holder_name,
                "has_pix": bool(pix_key),
            }
        )
