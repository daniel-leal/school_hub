"""
Admin configuration for classes app.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import ClassInvitation, ClassMember, SchoolClass, Student


class ClassMemberInline(TabularInline):
    """Inline for class members."""

    model = ClassMember
    extra = 0
    autocomplete_fields = ["guardian"]
    readonly_fields = ["joined_at"]


class StudentInline(TabularInline):
    """Inline for students."""

    model = Student
    extra = 0
    autocomplete_fields = ["guardian"]


@admin.register(SchoolClass)
class SchoolClassAdmin(ModelAdmin):
    """Admin configuration for SchoolClass model."""

    list_display = ["name", "school", "year", "member_count", "student_count", "is_active"]
    list_filter = ["year", "is_active"]
    search_fields = ["name", "school"]
    ordering = ["-year", "name"]
    readonly_fields = ["invite_code"]
    inlines = [ClassMemberInline, StudentInline]

    fieldsets = (
        (
            "Informações da Turma",
            {"fields": ("name", "school", "year", "description")},
        ),
        (
            "Configurações",
            {"fields": ("is_active", "invite_code")},
        ),
    )

    @admin.display(description="Membros")
    def member_count(self, obj):
        return obj.member_count

    @admin.display(description="Alunos")
    def student_count(self, obj):
        return obj.student_count


@admin.register(ClassMember)
class ClassMemberAdmin(ModelAdmin):
    """Admin configuration for ClassMember model."""

    list_display = ["guardian", "school_class", "role", "joined_at"]
    list_filter = ["role", "school_class"]
    search_fields = ["guardian__user__first_name", "guardian__user__last_name"]
    autocomplete_fields = ["guardian", "school_class"]


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    """Admin configuration for Student model."""

    list_display = ["name", "school_class", "guardian", "birth_date"]
    list_filter = ["school_class"]
    search_fields = ["name", "guardian__user__first_name"]
    autocomplete_fields = ["guardian", "school_class"]

    fieldsets = (
        (
            "Informações do Aluno",
            {"fields": ("name", "birth_date")},
        ),
        (
            "Vínculos",
            {"fields": ("school_class", "guardian")},
        ),
        (
            "Observações",
            {"fields": ("notes",)},
        ),
    )


@admin.register(ClassInvitation)
class ClassInvitationAdmin(ModelAdmin):
    """Admin configuration for ClassInvitation model."""

    list_display = ["school_class", "email", "status", "invited_by", "expires_at"]
    list_filter = ["status", "school_class"]
    search_fields = ["email", "school_class__name"]
    readonly_fields = ["token", "accepted_at", "accepted_by"]
    autocomplete_fields = ["school_class", "invited_by"]

    fieldsets = (
        (
            "Convite",
            {"fields": ("school_class", "email", "invited_by")},
        ),
        (
            "Status",
            {"fields": ("status", "expires_at", "token")},
        ),
        (
            "Aceitação",
            {"fields": ("accepted_at", "accepted_by")},
        ),
    )
