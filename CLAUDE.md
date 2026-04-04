# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Development
make run              # Start dev server (python manage.py runserver)
make migrate          # Apply migrations
make makemigrations   # Create migrations
make superuser        # Create superuser

# Code quality
make lint             # ruff check .
make lint-fix         # ruff check --fix .
make format           # ruff format .
make check            # lint + format-check
make typecheck        # pyright

# Testing
make test             # pytest
make test-v           # pytest -v (verbose)
make test-cov         # pytest --cov=apps
make test-fast        # pytest --reuse-db

# Single test
.venv/bin/pytest apps/events/tests/test_views.py::TestClassName::test_method_name -v

# Docker
make docker-up-d      # Start containers in background
make docker-migrate   # Run migrations in Docker
```

## Architecture

Django 5.1 project following **DDD + SOLID + Object Calisthenics**. Code is in English; UI is in **Portuguese (Brazil)**.

### Apps (`apps/`)

| App | Responsibility |
|-----|---------------|
| `core` | Base models (UUID, timestamps, soft-delete), `PixService`, DI container |
| `accounts` | Custom email-based `User` + `Guardian` profile (parent/responsible) |
| `classes` | `SchoolClass`, `ClassMember` (roles: admin/member), `Student`, invitation flow |
| `events` | `Event`, `EventItem`, `Payment` (with receipt upload), `EventParticipation` |
| `suppliers` | `Supplier` + `SupplierCategory` with WhatsApp/Instagram/Maps links |
| `dashboard` | Aggregated stats view (expenses, upcoming events, pending payments) |

### Key Model Relationships

```
User (1) ←→ (1) Guardian
Guardian (many) ←→ (many) SchoolClass  [through ClassMember]
Guardian (1) → (many) Student          [linked to a class]
SchoolClass (1) → (many) Event
Event (1) → (many) EventItem | Payment | EventParticipation
```

### Event Types
Events have 3 types: `PAYMENT`, `POTLUCK`, `PRESENCE`. Payments use PIX (EMV standard) with QR code generation via `PixService`.

### Dependency Injection
`apps/core/containers.py` defines `CoreContainer` (using `dependency-injector`). `PixService` is registered as a Singleton and injected into event views. Add new services here.

### Base Models
All models inherit from `BaseModel` (`apps/core/models.py`), which provides UUID primary key, `created_at`, `updated_at`, and soft-delete via `SoftDeleteManager`.

### Settings
Three-tier: `config/settings/base.py` + `dev.py` + `prod.py`. Environment variables via `python-decouple`. Key vars: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `PIX_KEY`, `PIX_MERCHANT_NAME`, `PIX_MERCHANT_CITY`.

### Admin
Uses **Django Unfold** with a custom sidebar and Portuguese labels. Dashboard stats are injected via a callback in `base.py`.

### Testing
Uses `pytest-django` with `factory-boy` + `faker` for fixtures. `--reuse-db` is the default for speed. Test files live alongside app code in `tests/` subdirectories.
