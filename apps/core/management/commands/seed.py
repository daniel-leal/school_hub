"""
Management command to seed the database with development data.

Usage:
    python manage.py seed          # Create seed data
    python manage.py seed --flush  # Clear and recreate seed data
"""

import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Guardian, User
from apps.classes.models import ClassMember, SchoolClass, Student
from apps.events.models import Event, EventItem, EventParticipation, Payment
from apps.suppliers.models import Supplier

PASSWORD = "seed1234"

GUARDIAN_DATA = [
    {
        "first_name": "Ana",
        "last_name": "Silva",
        "email": "ana.silva@example.com",
        "phone": "(11) 99001-0001",
    },
    {
        "first_name": "Bruno",
        "last_name": "Santos",
        "email": "bruno.santos@example.com",
        "phone": "(11) 99001-0002",
    },
    {
        "first_name": "Carla",
        "last_name": "Oliveira",
        "email": "carla.oliveira@example.com",
        "phone": "(11) 99001-0003",
    },
    {
        "first_name": "Diego",
        "last_name": "Pereira",
        "email": "diego.pereira@example.com",
        "phone": "(11) 99001-0004",
    },
    {
        "first_name": "Elena",
        "last_name": "Costa",
        "email": "elena.costa@example.com",
        "phone": "(11) 99001-0005",
    },
    {
        "first_name": "Felipe",
        "last_name": "Souza",
        "email": "felipe.souza@example.com",
        "phone": "(11) 99001-0006",
    },
    {
        "first_name": "Gabriela",
        "last_name": "Lima",
        "email": "gabriela.lima@example.com",
        "phone": "(11) 99001-0007",
    },
    {
        "first_name": "Henrique",
        "last_name": "Almeida",
        "email": "henrique.almeida@example.com",
        "phone": "(11) 99001-0008",
    },
    {
        "first_name": "Isabela",
        "last_name": "Ferreira",
        "email": "isabela.ferreira@example.com",
        "phone": "(11) 99001-0009",
    },
    {
        "first_name": "João",
        "last_name": "Rodrigues",
        "email": "joao.rodrigues@example.com",
        "phone": "(11) 99001-0010",
    },
]

CLASS_DATA = [
    {"name": "Turma A - 1º Ano", "school": "Escola Estrela Brilhante", "year": 2026},
    {"name": "Turma B - 2º Ano", "school": "Escola Estrela Brilhante", "year": 2026},
    {"name": "Turma C - 3º Ano", "school": "Colégio Novo Horizonte", "year": 2026},
]

# Maps guardian index -> class index. First 3 are admins.
MEMBERSHIP_MAP = [
    (0, 0, ClassMember.Role.ADMIN),
    (1, 1, ClassMember.Role.ADMIN),
    (2, 2, ClassMember.Role.ADMIN),
    (3, 0, ClassMember.Role.MEMBER),
    (4, 0, ClassMember.Role.MEMBER),
    (5, 1, ClassMember.Role.MEMBER),
    (6, 1, ClassMember.Role.MEMBER),
    (7, 2, ClassMember.Role.MEMBER),
    (8, 2, ClassMember.Role.MEMBER),
    (9, 0, ClassMember.Role.MEMBER),
]

# (name, guardian_index, class_index, birth_date)
# Some birth_dates in current month to test birthday feature
today = datetime.date.today()
STUDENT_DATA = [
    ("Lucas Silva", 0, 0, today.replace(day=5)),
    ("Maria Silva", 0, 0, today.replace(day=20)),
    ("Pedro Santos", 1, 1, datetime.date(2019, 6, 15)),
    ("Julia Oliveira", 2, 2, today.replace(day=12)),
    ("Rafael Pereira", 3, 0, datetime.date(2020, 1, 8)),
    ("Beatriz Costa", 4, 0, datetime.date(2020, 4, 22)),
    ("Mateus Souza", 5, 1, today.replace(day=28)),
    ("Sofia Lima", 6, 1, datetime.date(2019, 9, 3)),
    ("Gabriel Almeida", 7, 2, datetime.date(2018, 11, 17)),
    ("Valentina Ferreira", 8, 2, datetime.date(2018, 7, 30)),
    ("Theo Rodrigues", 9, 0, datetime.date(2020, 3, 14)),
    ("Laura Almeida", 7, 2, today.replace(day=1)),
]

SUPPLIER_DATA = [
    {
        "name": "Buffet Festa Feliz",
        "category": "Buffet",
        "contact_name": "Márcia Ribeiro",
        "phone": "(11) 3456-7890",
        "whatsapp": "(11) 93456-7890",
        "instagram": "buffetfestafeliz",
        "description": "Buffet infantil completo com salgados, doces e bolo.",
        "address": "Rua das Flores, 123 - São Paulo, SP",
        "rating": 5,
        "is_recommended": True,
    },
    {
        "name": "Papelaria Criativa",
        "category": "Papelaria",
        "contact_name": "Roberto Mendes",
        "phone": "(11) 3456-1234",
        "whatsapp": "(11) 93456-1234",
        "instagram": "papelariacriativa",
        "description": "Material escolar, lembrancinhas e convites personalizados.",
        "address": "Av. Paulista, 456 - São Paulo, SP",
        "rating": 4,
        "is_recommended": True,
    },
    {
        "name": "Foto & Vídeo Studio",
        "category": "Fotografia",
        "contact_name": "Camila Andrade",
        "phone": "(11) 3456-5678",
        "whatsapp": "(11) 93456-5678",
        "instagram": "fotovideostudio",
        "description": "Cobertura fotográfica e filmagem de eventos escolares.",
        "address": "Rua Augusta, 789 - São Paulo, SP",
        "rating": 5,
        "is_recommended": False,
    },
    {
        "name": "Brinquedos & Cia",
        "category": "Entretenimento",
        "contact_name": "Paulo Freitas",
        "phone": "(11) 3456-9012",
        "whatsapp": "(11) 93456-9012",
        "instagram": "brinquedosecia",
        "description": "Aluguel de brinquedos infláveis, pula-pula e recreação.",
        "address": "Rua Consolação, 321 - São Paulo, SP",
        "rating": 4,
        "is_recommended": True,
    },
]


class Command(BaseCommand):
    help = "Seed the database with development data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Clear existing seed data before creating new data",
        )

    @transaction.atomic
    def handle(self, *args, **options):  # noqa: ARG002
        if options["flush"]:
            self._flush()

        guardians = self._create_guardians()
        classes = self._create_classes()
        self._create_memberships(guardians, classes)
        students = self._create_students(guardians, classes)
        self._create_events(guardians, classes, students)
        self._create_suppliers()

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))
        self.stdout.write(f"  Password for all users: {PASSWORD}")
        self.stdout.write("  Users:")
        for g in guardians:
            self.stdout.write(f"    - {g.user.email}")

    def _flush(self):
        self.stdout.write("Flushing existing seed data...")
        emails = [g["email"] for g in GUARDIAN_DATA]
        User.objects.filter(email__in=emails).delete()
        Supplier.objects.filter(name__in=[s["name"] for s in SUPPLIER_DATA]).delete()
        SchoolClass.objects.filter(name__in=[c["name"] for c in CLASS_DATA], year=2026).delete()
        self.stdout.write(self.style.SUCCESS("Flushed."))

    def _create_guardians(self):
        guardians = []
        for data in GUARDIAN_DATA:
            if User.objects.filter(email=data["email"]).exists():
                user = User.objects.get(email=data["email"])
                guardian = user.guardian
            else:
                user = User.objects.create_user(
                    email=data["email"],
                    password=PASSWORD,
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data["phone"],
                )
                guardian = Guardian.objects.create(user=user)
            guardians.append(guardian)
        self.stdout.write(f"  Created {len(guardians)} guardians")
        return guardians

    def _create_classes(self):
        classes = []
        for data in CLASS_DATA:
            school_class, _ = SchoolClass.objects.get_or_create(
                name=data["name"],
                year=data["year"],
                defaults={"school": data["school"]},
            )
            classes.append(school_class)
        self.stdout.write(f"  Created {len(classes)} classes")
        return classes

    def _create_memberships(self, guardians, classes):
        count = 0
        for guardian_idx, class_idx, role in MEMBERSHIP_MAP:
            _, created = ClassMember.objects.get_or_create(
                school_class=classes[class_idx],
                guardian=guardians[guardian_idx],
                defaults={"role": role},
            )
            if created:
                count += 1
        self.stdout.write(f"  Created {count} memberships")

    def _create_students(self, guardians, classes):
        students = []
        for name, guardian_idx, class_idx, birth_date in STUDENT_DATA:
            student, _ = Student.objects.get_or_create(
                name=name,
                guardian=guardians[guardian_idx],
                defaults={
                    "school_class": classes[class_idx],
                    "birth_date": birth_date,
                },
            )
            students.append(student)
        self.stdout.write(f"  Created {len(students)} students")
        return students

    def _create_events(self, guardians, classes, _students):
        # Event 1: PAYMENT event in Class A
        evt_payment, _ = Event.objects.get_or_create(
            title="Festa Junina 2026",
            school_class=classes[0],
            defaults={
                "created_by": guardians[0],
                "description": "Festa junina da turma com comidas típicas, brincadeiras e quadrilha.",
                "event_type": Event.EventType.PAYMENT,
                "event_date": datetime.date(2026, 6, 20),
                "location": "Pátio da Escola Estrela Brilhante",
                "budget": Decimal("500.00"),
                "individual_amount": Decimal("100.00"),
                "pix_key": "ana.silva@example.com",
                "pix_holder_name": "Ana Silva",
                "responsible": guardians[0],
            },
        )

        # Payments for the PAYMENT event
        class_a_guardians = [guardians[i] for i, c, _ in MEMBERSHIP_MAP if c == 0]
        for i, guardian in enumerate(class_a_guardians):
            student_count = guardian.students.filter(school_class=classes[0]).count()
            amount = evt_payment.individual_amount * student_count
            payment, created = Payment.objects.get_or_create(
                event=evt_payment,
                guardian=guardian,
                defaults={
                    "amount": amount,
                    "status": Payment.Status.CONFIRMED if i < 2 else Payment.Status.PENDING,
                },
            )
            if created and payment.status == Payment.Status.CONFIRMED:
                payment.confirmed_by = guardians[0]
                payment.confirmed_at = timezone.now()
                payment.save(update_fields=["confirmed_by", "confirmed_at"])

        # Event 2: POTLUCK event in Class B
        evt_potluck, _ = Event.objects.get_or_create(
            title="Piquenique no Parque",
            school_class=classes[1],
            defaults={
                "created_by": guardians[1],
                "description": "Piquenique de integração das famílias no Parque Ibirapuera.",
                "event_type": Event.EventType.POTLUCK,
                "event_date": datetime.date(2026, 4, 18),
                "location": "Parque Ibirapuera - Portão 3",
            },
        )

        # Items for POTLUCK event
        potluck_items = [
            ("Pão de queijo", guardians[1]),
            ("Suco de uva", guardians[5]),
            ("Biscoitos", guardians[6]),
            ("Frutas", None),
        ]
        for name, assigned in potluck_items:
            EventItem.objects.get_or_create(
                event=evt_potluck,
                name=name,
                defaults={
                    "item_type": EventItem.ItemType.CONTRIBUTION,
                    "quantity": 1,
                    "assigned_to": assigned,
                    "is_completed": assigned is not None,
                },
            )

        # Participations for POTLUCK
        class_b_guardians = [guardians[i] for i, c, _ in MEMBERSHIP_MAP if c == 1]
        contributions = ["Pão de queijo", "Suco de uva", "Biscoitos", ""]
        for i, guardian in enumerate(class_b_guardians):
            participation, created = EventParticipation.objects.get_or_create(
                event=evt_potluck,
                guardian=guardian,
                defaults={
                    "status": EventParticipation.Status.CONFIRMED if i < 2 else EventParticipation.Status.PENDING,
                    "contribution": contributions[i] if i < len(contributions) else "",
                    "guests_count": 2,
                },
            )
            if created and participation.status == EventParticipation.Status.CONFIRMED:
                participation.confirmed_at = timezone.now()
                participation.save(update_fields=["confirmed_at"])

        # Event 3: PRESENCE event in Class C
        evt_presence, _ = Event.objects.get_or_create(
            title="Reunião de Pais",
            school_class=classes[2],
            defaults={
                "created_by": guardians[2],
                "description": "Reunião de pais e mestres para discussão do calendário escolar.",
                "event_type": Event.EventType.PRESENCE,
                "event_date": datetime.date(2026, 5, 10),
                "location": "Sala de reuniões - Colégio Novo Horizonte",
            },
        )

        # Participations for PRESENCE
        class_c_guardians = [guardians[i] for i, c, _ in MEMBERSHIP_MAP if c == 2]
        for i, guardian in enumerate(class_c_guardians):
            participation, created = EventParticipation.objects.get_or_create(
                event=evt_presence,
                guardian=guardian,
                defaults={
                    "status": EventParticipation.Status.CONFIRMED if i < 2 else EventParticipation.Status.PENDING,
                    "guests_count": 1,
                },
            )
            if created and participation.status == EventParticipation.Status.CONFIRMED:
                participation.confirmed_at = timezone.now()
                participation.save(update_fields=["confirmed_at"])

        # Event 4: MIXED event in Class A
        evt_mixed, _ = Event.objects.get_or_create(
            title="Festa de Encerramento",
            school_class=classes[0],
            defaults={
                "created_by": guardians[0],
                "description": "Festa de encerramento do ano letivo com lanche e atividades.",
                "event_type": Event.EventType.MIXED,
                "event_date": datetime.date(2026, 12, 5),
                "location": "Escola Estrela Brilhante - Quadra",
                "budget": Decimal("800.00"),
                "individual_amount": Decimal("160.00"),
                "pix_key": "ana.silva@example.com",
                "pix_holder_name": "Ana Silva",
                "responsible": guardians[0],
            },
        )

        # Items for MIXED event
        mixed_items = [
            ("Decoração", EventItem.ItemType.EXPENSE, Decimal("150.00"), None),
            ("Bolo", EventItem.ItemType.CONTRIBUTION, None, guardians[3]),
            ("Refrigerantes", EventItem.ItemType.CONTRIBUTION, None, guardians[4]),
            ("Salgados", EventItem.ItemType.EXPENSE, Decimal("200.00"), None),
        ]
        for name, item_type, price, assigned in mixed_items:
            EventItem.objects.get_or_create(
                event=evt_mixed,
                name=name,
                defaults={
                    "item_type": item_type,
                    "quantity": 1,
                    "unit_price": price,
                    "assigned_to": assigned,
                    "is_completed": False,
                },
            )

        # Payments for MIXED event
        for i, guardian in enumerate(class_a_guardians):
            student_count = guardian.students.filter(school_class=classes[0]).count()
            amount = evt_mixed.individual_amount * student_count
            Payment.objects.get_or_create(
                event=evt_mixed,
                guardian=guardian,
                defaults={
                    "amount": amount,
                    "status": Payment.Status.CONFIRMED if i == 0 else Payment.Status.PENDING,
                },
            )

        # Participations for MIXED event
        for i, guardian in enumerate(class_a_guardians):
            EventParticipation.objects.get_or_create(
                event=evt_mixed,
                guardian=guardian,
                defaults={
                    "status": EventParticipation.Status.CONFIRMED if i == 0 else EventParticipation.Status.PENDING,
                    "guests_count": 2,
                },
            )

        self.stdout.write("  Created 4 events with payments, items, and participations")

    def _create_suppliers(self):
        count = 0
        for data in SUPPLIER_DATA:
            _, created = Supplier.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if created:
                count += 1
        self.stdout.write(f"  Created {count} suppliers")
