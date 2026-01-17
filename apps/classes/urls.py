"""
URL configuration for classes app.
"""

from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    # Class list and detail
    path("", views.ClassListView.as_view(), name="list"),
    path("nova/", views.ClassCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.ClassDetailView.as_view(), name="detail"),
    path("<uuid:pk>/editar/", views.ClassUpdateView.as_view(), name="update"),
    # Students
    path("<uuid:class_id>/alunos/novo/", views.StudentCreateView.as_view(), name="student_create"),
    path("alunos/<uuid:pk>/editar/", views.StudentUpdateView.as_view(), name="student_update"),
    path("alunos/<uuid:pk>/excluir/", views.StudentDeleteView.as_view(), name="student_delete"),
    # Invitations
    path("convite/<str:token>/", views.AcceptInvitationView.as_view(), name="accept_invitation"),
    path("<uuid:pk>/convidar/", views.CreateInvitationView.as_view(), name="create_invitation"),
    path("entrar/", views.JoinClassView.as_view(), name="join"),
]
