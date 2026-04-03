# ruff: noqa: ARG002
"""
Tests for the dashboard views.
"""

import datetime

import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import Guardian, User
from apps.classes.models import ClassMember, SchoolClass, Student


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="guardian@test.com",
        password="password123",
        first_name="Test",
    )


@pytest.fixture
def guardian(user):
    return Guardian.objects.create(user=user)


@pytest.fixture
def school_class(db):
    return SchoolClass.objects.create(name="Turma A", description="Test class")


@pytest.fixture
def membership(guardian, school_class):
    return ClassMember.objects.create(
        guardian=guardian,
        school_class=school_class,
        role=ClassMember.Role.MEMBER,
    )


@pytest.fixture
def client_logged_in(user):
    client = Client()
    client.login(email="guardian@test.com", password="password123")
    return client


@pytest.mark.django_db
class TestDashboardBirthdays:
    url = reverse("dashboard:index")

    def test_student_with_birthday_this_month_appears(self, client_logged_in, guardian, school_class, membership):
        today = datetime.date.today()
        student = Student.objects.create(
            name="Ana",
            school_class=school_class,
            guardian=guardian,
            birth_date=today.replace(day=15) if today.day != 15 else today.replace(day=14),
        )

        response = client_logged_in.get(self.url)

        assert response.status_code == 200
        assert student in list(response.context["birthdays"])

    def test_student_with_birthday_other_month_excluded(self, client_logged_in, guardian, school_class, membership):
        today = datetime.date.today()
        other_month = 1 if today.month != 1 else 2
        student = Student.objects.create(
            name="Bruno",
            school_class=school_class,
            guardian=guardian,
            birth_date=today.replace(month=other_month, day=10),
        )

        response = client_logged_in.get(self.url)

        assert response.status_code == 200
        assert student not in list(response.context["birthdays"])

    def test_student_without_birth_date_excluded(self, client_logged_in, guardian, school_class, membership):
        student = Student.objects.create(
            name="Carlos",
            school_class=school_class,
            guardian=guardian,
            birth_date=None,
        )

        response = client_logged_in.get(self.url)

        assert response.status_code == 200
        assert student not in list(response.context["birthdays"])

    def test_empty_birthdays_context_when_none_this_month(self, client_logged_in, guardian, school_class, membership):
        today = datetime.date.today()
        other_month = 1 if today.month != 1 else 2
        Student.objects.create(
            name="Diana",
            school_class=school_class,
            guardian=guardian,
            birth_date=today.replace(month=other_month, day=5),
        )

        response = client_logged_in.get(self.url)

        assert response.status_code == 200
        assert list(response.context["birthdays"]) == []

    def test_birthdays_ordered_by_day(self, client_logged_in, guardian, school_class, membership):
        today = datetime.date.today()

        def make_date(day):
            return datetime.date(2000, today.month, day)

        s1 = Student.objects.create(
            name="Eduardo",
            school_class=school_class,
            guardian=guardian,
            birth_date=make_date(20),
        )
        s2 = Student.objects.create(
            name="Fernanda",
            school_class=school_class,
            guardian=guardian,
            birth_date=make_date(5),
        )
        s3 = Student.objects.create(
            name="Gabi",
            school_class=school_class,
            guardian=guardian,
            birth_date=make_date(12),
        )

        response = client_logged_in.get(self.url)
        birthdays = list(response.context["birthdays"])

        assert birthdays.index(s2) < birthdays.index(s3) < birthdays.index(s1)

    def test_students_from_other_guardian_classes_appear(self, client_logged_in, guardian, school_class, membership, db):
        """Students from classmates (not direct children) should appear."""
        today = datetime.date.today()

        other_user = User.objects.create_user(email="other@test.com", password="pw", first_name="Other")
        other_guardian = Guardian.objects.create(user=other_user)

        classmate_student = Student.objects.create(
            name="Helena",
            school_class=school_class,
            guardian=other_guardian,
            birth_date=today.replace(day=10) if today.day != 10 else today.replace(day=11),
        )

        response = client_logged_in.get(self.url)
        birthdays = list(response.context["birthdays"])

        assert classmate_student in birthdays
