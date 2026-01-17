FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/ requirements/
ARG ENVIRONMENT=prod
RUN pip install -r requirements/${ENVIRONMENT}.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.prod || true

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]
