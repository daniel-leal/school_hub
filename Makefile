# School Hub - Makefile
# =====================

.PHONY: help install run migrate makemigrations shell superuser collectstatic \
        docker-build docker-up docker-down docker-logs docker-shell docker-migrate \
        docker-makemigrations docker-superuser lint format test clean

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
MANAGE := $(PYTHON) manage.py
DOCKER_COMPOSE := docker compose

# =============================================================================
# HELP
# =============================================================================

help: ## Show this help message
	@echo "School Hub - Available Commands"
	@echo "================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================

install: ## Install Python dependencies (dev)
	pip install -r requirements/dev.txt

run: ## Run the development server
	$(MANAGE) runserver

runserver: run ## Alias for run

migrate: ## Apply database migrations
	$(MANAGE) migrate

makemigrations: ## Create new migrations
	$(MANAGE) makemigrations

migrations: makemigrations ## Alias for makemigrations

shell: ## Open Django shell
	$(MANAGE) shell

shell-plus: ## Open Django shell_plus (if django-extensions installed)
	$(MANAGE) shell_plus

superuser: ## Create a superuser
	$(MANAGE) createsuperuser

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

showmigrations: ## Show all migrations and their status
	$(MANAGE) showmigrations

flush: ## Flush the database
	$(MANAGE) flush --noinput

# =============================================================================
# DOCKER COMMANDS
# =============================================================================

docker-build: ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-up: ## Start Docker containers
	$(DOCKER_COMPOSE) up

docker-up-d: ## Start Docker containers in detached mode
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop Docker containers
	$(DOCKER_COMPOSE) down

docker-down-v: ## Stop Docker containers and remove volumes
	$(DOCKER_COMPOSE) down -v

docker-restart: ## Restart Docker containers
	$(DOCKER_COMPOSE) restart

docker-logs: ## View Docker container logs
	$(DOCKER_COMPOSE) logs -f

docker-logs-web: ## View web container logs
	$(DOCKER_COMPOSE) logs -f web

docker-logs-db: ## View database container logs
	$(DOCKER_COMPOSE) logs -f db

docker-shell: ## Open shell in web container
	$(DOCKER_COMPOSE) exec web /bin/bash

docker-django-shell: ## Open Django shell in web container
	$(DOCKER_COMPOSE) exec web python manage.py shell

docker-migrate: ## Run migrations in Docker
	$(DOCKER_COMPOSE) exec web python manage.py migrate

docker-makemigrations: ## Create migrations in Docker
	$(DOCKER_COMPOSE) exec web python manage.py makemigrations

docker-superuser: ## Create superuser in Docker
	$(DOCKER_COMPOSE) exec web python manage.py createsuperuser

docker-ps: ## Show running Docker containers
	$(DOCKER_COMPOSE) ps

docker-prune: ## Remove unused Docker resources
	docker system prune -f

# =============================================================================
# CODE QUALITY
# =============================================================================

lint: ## Run ruff linter
	ruff check .

lint-fix: ## Run ruff linter with auto-fix
	ruff check --fix .

format: ## Format code with ruff
	ruff format .

format-check: ## Check code formatting without changes
	ruff format --check .

typecheck: ## Run type checking with pyright
	pyright

check: lint format-check ## Run all code quality checks

fix: lint-fix format ## Fix all auto-fixable issues

# =============================================================================
# TESTING
# =============================================================================

test: ## Run tests
	pytest

test-v: ## Run tests with verbose output
	pytest -v

test-cov: ## Run tests with coverage report
	pytest --cov=apps --cov-report=term-missing

test-fast: ## Run tests without database recreation
	pytest --reuse-db

# =============================================================================
# UTILITIES
# =============================================================================

clean: ## Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

reset-db: ## Reset the database (WARNING: destroys all data)
	$(MANAGE) flush --noinput
	$(MANAGE) migrate

docker-reset-db: ## Reset Docker database (WARNING: destroys all data)
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d db
	sleep 5
	$(DOCKER_COMPOSE) up -d web
	$(DOCKER_COMPOSE) exec web python manage.py migrate

dump-data: ## Dump database data to JSON
	$(MANAGE) dumpdata --indent 2 > data.json

load-data: ## Load database data from JSON
	$(MANAGE) loaddata data.json

# =============================================================================
# COMBINED COMMANDS
# =============================================================================

fresh: clean install migrate ## Clean install and migrate

docker-fresh: docker-down-v docker-build docker-up ## Fresh Docker build and start

dev: docker-up ## Start development environment (Docker)

setup: install migrate superuser ## Initial project setup
