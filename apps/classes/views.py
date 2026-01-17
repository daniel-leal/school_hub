"""
Views for classes app.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from apps.accounts.models import Guardian

from .forms import ClassForm, InvitationForm, JoinClassForm, StudentForm
from .models import ClassInvitation, ClassMember, SchoolClass, Student


class ClassListView(LoginRequiredMixin, ListView):
    """List all classes the user is a member of."""

    model = SchoolClass
    template_name = "classes/class_list.html"
    context_object_name = "classes"
    paginate_by = 12

    def get_queryset(self):
        guardian = getattr(self.request.user, "guardian", None)
        if guardian:
            return SchoolClass.objects.filter(
                members__guardian=guardian,
                is_active=True,
            ).distinct()
        return SchoolClass.objects.none()


class ClassDetailView(LoginRequiredMixin, DetailView):
    """View class details."""

    model = SchoolClass
    template_name = "classes/class_detail.html"
    context_object_name = "school_class"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guardian = getattr(self.request.user, "guardian", None)

        context["is_member"] = False
        context["is_admin"] = False
        context["my_students"] = []

        if guardian:
            membership = self.object.members.filter(guardian=guardian).first()
            if membership:
                context["is_member"] = True
                context["is_admin"] = membership.is_admin
                context["my_students"] = self.object.students.filter(guardian=guardian)

        context["members"] = self.object.members.select_related(
            "guardian__user"
        ).order_by("guardian__user__first_name")
        context["students"] = self.object.students.select_related(
            "guardian__user"
        ).order_by("name")
        context["events"] = self.object.events.filter(is_active=True).order_by("-event_date")[:5]

        return context


class ClassCreateView(LoginRequiredMixin, CreateView):
    """Create a new class."""

    model = SchoolClass
    form_class = ClassForm
    template_name = "classes/class_form.html"

    def form_valid(self, form):
        guardian = getattr(self.request.user, "guardian", None)
        if not guardian:
            Guardian.objects.create(user=self.request.user)
            guardian = self.request.user.guardian

        with transaction.atomic():
            self.object = form.save()
            # Add creator as admin
            ClassMember.objects.create(
                school_class=self.object,
                guardian=guardian,
                role=ClassMember.Role.ADMIN,
            )

        messages.success(
            self.request,
            f'Turma "{self.object.name}" criada com sucesso! '
            f"Código de convite: {self.object.invite_code}",
        )
        return redirect("classes:detail", pk=self.object.pk)


class ClassUpdateView(LoginRequiredMixin, UpdateView):
    """Update class details."""

    model = SchoolClass
    form_class = ClassForm
    template_name = "classes/class_form.html"

    def get_success_url(self):
        return reverse_lazy("classes:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Turma atualizada com sucesso!")
        return super().form_valid(form)


class StudentCreateView(LoginRequiredMixin, CreateView):
    """Add a student to a class."""

    model = Student
    form_class = StudentForm
    template_name = "classes/student_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_class"] = get_object_or_404(
            SchoolClass, pk=self.kwargs["class_id"]
        )
        return context

    def form_valid(self, form):
        guardian = getattr(self.request.user, "guardian", None)
        school_class = get_object_or_404(SchoolClass, pk=self.kwargs["class_id"])

        self.object = form.save(commit=False)
        self.object.guardian = guardian
        self.object.school_class = school_class
        self.object.save()

        messages.success(self.request, f'Aluno "{self.object.name}" adicionado!')
        return redirect("classes:detail", pk=school_class.pk)


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    """Update student details."""

    model = Student
    form_class = StudentForm
    template_name = "classes/student_form.html"

    def get_queryset(self):
        guardian = getattr(self.request.user, "guardian", None)
        return Student.objects.filter(guardian=guardian)

    def get_success_url(self):
        return reverse_lazy("classes:detail", kwargs={"pk": self.object.school_class.pk})

    def form_valid(self, form):
        messages.success(self.request, "Aluno atualizado com sucesso!")
        return super().form_valid(form)


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a student."""

    model = Student
    template_name = "classes/student_confirm_delete.html"

    def get_queryset(self):
        guardian = getattr(self.request.user, "guardian", None)
        return Student.objects.filter(guardian=guardian)

    def get_success_url(self):
        return reverse_lazy("classes:detail", kwargs={"pk": self.object.school_class.pk})

    def form_valid(self, form):
        messages.success(self.request, "Aluno removido com sucesso!")
        return super().form_valid(form)


class AcceptInvitationView(LoginRequiredMixin, View):
    """Accept a class invitation."""

    def get(self, request, token):
        invitation = get_object_or_404(ClassInvitation, token=token)

        if not invitation.is_valid:
            messages.error(request, "Este convite não é mais válido.")
            return redirect("classes:list")

        guardian = getattr(request.user, "guardian", None)
        if not guardian:
            guardian = Guardian.objects.create(user=request.user)

        try:
            invitation.accept(guardian)
            messages.success(
                request,
                f'Você agora faz parte da turma "{invitation.school_class.name}"!',
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect("classes:detail", pk=invitation.school_class.pk)


class CreateInvitationView(LoginRequiredMixin, CreateView):
    """Create a class invitation."""

    model = ClassInvitation
    form_class = InvitationForm
    template_name = "classes/invitation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_class"] = get_object_or_404(SchoolClass, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        school_class = get_object_or_404(SchoolClass, pk=self.kwargs["pk"])
        guardian = getattr(self.request.user, "guardian", None)

        self.object = form.save(commit=False)
        self.object.school_class = school_class
        self.object.invited_by = guardian
        self.object.save()

        invite_url = self.request.build_absolute_uri(
            reverse_lazy("classes:accept_invitation", kwargs={"token": self.object.token})
        )

        messages.success(
            self.request,
            f"Convite criado! Link: {invite_url}",
        )
        return redirect("classes:detail", pk=school_class.pk)


class JoinClassView(LoginRequiredMixin, FormView):
    """Join a class using invite code."""

    form_class = JoinClassForm
    template_name = "classes/join_class.html"
    success_url = reverse_lazy("classes:list")

    def form_valid(self, form):
        code = form.cleaned_data["invite_code"]
        school_class = SchoolClass.objects.filter(invite_code=code, is_active=True).first()

        if not school_class:
            messages.error(self.request, "Código de convite inválido.")
            return self.form_invalid(form)

        guardian = getattr(self.request.user, "guardian", None)
        if not guardian:
            guardian = Guardian.objects.create(user=self.request.user)

        membership, created = ClassMember.objects.get_or_create(
            school_class=school_class,
            guardian=guardian,
            defaults={"role": ClassMember.Role.MEMBER},
        )

        if created:
            messages.success(
                self.request,
                f'Você entrou na turma "{school_class.name}"!',
            )
        else:
            messages.info(
                self.request,
                f'Você já é membro da turma "{school_class.name}".',
            )

        return redirect("classes:detail", pk=school_class.pk)
