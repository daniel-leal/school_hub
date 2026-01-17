# School Hub 🎓

Platform for managing school events for parents and guardians.

## 📋 Summary

**School Hub** is a Django application developed to solve the problem of organizing school events that are currently managed in WhatsApp groups.

### Problem

School events are managed by parents in WhatsApp groups, where there is no proper organization, creating difficulties in managing payments and parallel events. For example, in one week there may be a Mother's Day event that requires purchasing stationery items and student clothing, while simultaneously parents decide to buy a gift for the teachers who are also mothers. This results in multiple bank transfers, with different parents responsible for each item. For each receipt sent, it's necessary to manually mark who has already made the transfer and who hasn't.

### Solution

School Hub centralizes all school event management in a single platform, offering:

- **Class Management**: Creation of classes and generic invitations for other parents
- **Flexible Events**: Support for financial collections, shared snacks, or mixed events
- **PIX Integration**: Automatic generation of PIX QR codes and payment links
- **Payment Management**: Receipt upload and automatic payment confirmation
- **Dashboard**: Overview of active events, totals, and expenses throughout the year
- **Suppliers**: Registration of useful contacts (seamstresses, decorators, etc.) with optional Google Maps integration

The application has two main areas:
- **Admin**: Django Admin interface with Django Unfold for complete management (CRUDs, areas, and contexts)
- **Parents Area**: Intuitive interface for event registration, items, event viewing, and payment management

## 🔧 Requirements

### System Requirements

- **Python**: 3.12+ (with virtual environment)
- **PostgreSQL**: 16+
- **Docker** (optional, but recommended): Docker and Docker Compose
- **Node.js** (optional): For frontend tools, if needed

### Python Dependencies

- **Django**: Main web framework
- **Django Unfold**: Modern interface for Django Admin
- **PostgreSQL**: Database (via psycopg2)
- **Ruff**: Linter and formatter
- **Pyright**: Type checker
- **Pytest**: Testing framework

Dependencies are organized by environment:
- `requirements/base.txt`: Common dependencies for all environments
- `requirements/dev.txt`: Development dependencies (includes base.txt)
- `requirements/prod.txt`: Production dependencies (includes base.txt)

## 🚀 Setup & How to Run

### Prerequisites

1. Python 3.12 installed
2. PostgreSQL 16 installed and running (if not using Docker)
3. Docker and Docker Compose installed (optional, but recommended)

### Option 1: With Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd school_hub
   ```

2. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit the .env file as needed
   ```

3. **Start the containers**:
   ```bash
   make docker-up-d
   # or
   docker-compose up -d
   ```

4. **Run migrations**:
   ```bash
   make docker-migrate
   # or
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   make docker-superuser
   # or
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**:
   - Frontend: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Option 2: Without Docker (Local Development)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd school_hub
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   make install
   # or
   pip install -r requirements/dev.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit the .env file with your settings
   # Make sure PostgreSQL is running and accessible
   ```

5. **Run migrations**:
   ```bash
   make migrate
   # or
   python manage.py migrate
   ```

6. **Create a superuser**:
   ```bash
   make superuser
   # or
   python manage.py createsuperuser
   ```

7. **Start the development server**:
   ```bash
   make run
   # or
   python manage.py runserver
   ```

8. **Access the application**:
   - Frontend: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Useful Commands (Makefile)

The project includes a Makefile with several useful commands:

```bash
# View all available commands
make help

# Development
make install          # Install dependencies
make run              # Run development server
make migrate          # Apply migrations
make makemigrations   # Create new migrations
make superuser        # Create superuser

# Docker
make docker-up-d      # Start containers in background
make docker-down      # Stop containers
make docker-logs      # View container logs
make docker-shell     # Open shell in web container
make docker-migrate   # Run migrations in Docker

# Code quality
make lint             # Check code with ruff
make format           # Format code
make typecheck        # Check types with pyright
make test             # Run tests
```

## 🔄 Workflow

### 1. Registration and Authentication

- A parent/guardian registers on the platform
- After registration, they can create a class or join an existing class using a generic invitation code
- The admin can also send generic invitations to parents

### 2. Class Management

- In the class area, any parent can:
  - Register students
  - View list of students and guardians
  - Manage invitations for the class

### 3. Event Creation

- Any parent can register an event in the class
- When creating an event, it's possible to:
  - Define event name, description, and date
  - Define total budget (optional, for events with collection)
  - Register PIX for payment (PIX key, beneficiary name)
  - Generate PIX QR code or link for sharing on WhatsApp
  - Add items to the event (with or without value)

### 4. Event Types

**Financial Collection Event**:
- Defines total budget
- Divides the amount among students
- Generates PIX QR code or payment link
- Parents upload receipt
- System automatically marks who has paid

**Shared Snack Event**:
- Does not require budget
- List of items that each parent/guardian will bring
- Each parent is responsible for one or more items

**Mixed Event**:
- Combines financial collection and items to be brought

### 5. Payment Management

- Logged-in parent selects the event
- Uploads receipt with the amount
- Transaction is automatically recorded in that event's payments
- System marks the parent as "paid" in the event
- All parents can view who has paid and who hasn't

### 6. Dashboard

- Overview in the guardian area:
  - Active events chart
  - Total events
  - Total expenses throughout the year
  - List of guardian's classes
  - Upcoming events

### 7. Suppliers

- Registration of useful contacts (seamstresses, decorators, catering, etc.)
- Contact information (phone, address)
- Optional Google Maps integration (latitude/longitude)

### 8. Admin Area

- Django Admin interface with Django Unfold
- Complete management of all entities
- CRUDs for all areas
- Dashboard with charts and statistics
- Fields like "Created At" and "Updated At" are not displayed in listings (only in details)

## 📁 Project Structure

```
school_hub/
├── apps/
│   ├── accounts/       # Users and guardians
│   ├── classes/        # Classes, students and invitations
│   ├── core/           # Base models and services
│   ├── dashboard/      # User dashboard
│   ├── events/         # Events and payments
│   └── suppliers/      # Suppliers
├── config/
│   ├── settings/       # Settings (base, dev, prod)
│   ├── urls.py
│   └── wsgi.py
├── templates/          # HTML templates
├── static/             # Static files
├── requirements/       # Dependencies by environment
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── manage.py
└── pyproject.toml
```

## 🏗️ Architecture

The project follows development best practices:

- **SOLID**: Object-oriented design principles
- **DDD (Domain-Driven Design)**: Organization by domains
- **Object Calisthenics**: Code best practices
- **Testing**: Unit and integration testing best practices
- **Environment Separation**: Separate configurations for dev/prod
- **Dependency Injection**: Use of containers and different implementations per environment
- **Query Optimization**: Avoids N+1 queries, use of transactions
- **Pagination**: Pagination system with page/size

## 🔐 Environment Variables

Main environment variables (see `env.example` for complete list):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | PostgreSQL URL | `postgres://school_hub:school_hub@localhost:5432/school_hub` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.dev` |
| `PIX_KEY` | PIX key (optional) | - |
| `PIX_MERCHANT_NAME` | PIX merchant name | - |
| `PIX_MERCHANT_CITY` | PIX merchant city | - |

## 🧪 Testing

```bash
# Run all tests
make test
# or
pytest

# Tests with coverage
make test-cov
# or
pytest --cov=apps --cov-report=term-missing

# Verbose tests
make test-v
# or
pytest -v
```

## 🔍 Code Quality

```bash
# Check linting
make lint
# or
ruff check .

# Format code
make format
# or
ruff format .

# Check types
make typecheck
# or
pyright

# Check everything
make check
```

## 📝 Important Notes

- **Language**: Fields on HTML pages are in Portuguese (eventos, turma, aluno, orçamento...), but the code is entirely written in English
- **Hidden Fields**: Fields like "Created At" and "Updated At" are not displayed in listing screens, only in details
- **Admin Interface**: Uses Django Unfold for a modern and intuitive UI
- **PIX**: The PIX integration allows generating QR codes and links for sharing on WhatsApp

## 📄 License

MIT

---

Made with 💜 for parents and schools.
