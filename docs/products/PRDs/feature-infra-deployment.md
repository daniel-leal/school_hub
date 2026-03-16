# PRD: Infrastructure & Deployment — School Hub

## Problem

School Hub lacks production-ready infrastructure for email delivery, file storage, and cloud deployment. Development is also limited by the absence of local substitutes for these services, making it impossible to test email flows or cloud-compatible storage without deploying to production.

## Target Users

- **DevOps / Developers** maintaining and deploying School Hub
- **End users** (guardians, school admins) who will benefit from transactional emails and reliable file storage

## Goals

1. Enable local development with production-parity services. You can use injection containers. (email via MailHog, storage via MinIO)
2. Implement transactional email features across the application
3. Migrate file storage from local filesystem to S3-compatible backend (MinIO locally, Cloudflare R2 in production)
4. Deploy the application to Fly.io with Supabase PostgreSQL, Cloudflare R2, and Resend

## Non-Goals

- CI/CD pipeline setup (GitHub Actions, etc.)
- Custom domain and SSL configuration
- CDN for static file delivery
- APM/monitoring beyond existing Sentry integration
- Changing the local PostgreSQL dev database (stays as-is)
- Implementing new application features beyond transactional emails

---

## Architecture Overview

```
LOCAL DEV                          PRODUCTION
─────────────────                  ─────────────────
Django (runserver)                  Django (Gunicorn) on Fly.io
PostgreSQL 16 (Docker)             Supabase PostgreSQL
MinIO (Docker, S3-compatible)      Cloudflare R2 (S3-compatible)
MailHog (Docker, SMTP + Web UI)    Resend (SMTP/API)
```

Both environments use `django-storages` with S3-compatible backends, and Django's SMTP email backend — only the connection settings differ.

---

## Phase 1 — Local Development Tooling

### US-1: MinIO for Local File Storage

**As a** developer, **I want** an S3-compatible local storage service, **so that** I can test file uploads without cloud dependencies.

**Acceptance Criteria:**

- [ ] MinIO service added to `docker-compose.yml` with persistent volume
- [ ] MinIO Console accessible at `localhost:9001` for browsing buckets
- [ ] A default bucket (e.g., `school-hub-media`) is created on startup (via init container or entrypoint script)
- [ ] `django-storages[s3]` and `boto3` added to `requirements/base.txt`
- [ ] Dev settings configure `storages.backends.s3boto3.S3Boto3Storage` pointing to local MinIO
- [ ] `Payment.receipt` uploads work end-to-end through MinIO
- [ ] Media files are served via MinIO presigned URLs or Django proxy in dev
- [ ] Existing `MEDIA_URL` / `MEDIA_ROOT` references updated where needed
- [ ] Environment variables: `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_BUCKET_NAME`, `STORAGE_ENDPOINT_URL`
- [ ] Django settings map these env vars to the `django-storages` S3Boto3 config (no `AWS_*` naming)

### US-2: MailHog for Local Email

**As a** developer, **I want** a local SMTP server with a web UI, **so that** I can inspect transactional emails during development.

**Acceptance Criteria:**

- [ ] MailHog service added to `docker-compose.yml`
- [ ] MailHog Web UI accessible at `localhost:8025`
- [ ] Dev settings configure Django's SMTP email backend pointing to MailHog (`localhost:1025`, no auth)
- [ ] Console email backend replaced by SMTP backend in `config/settings/dev.py`
- [ ] Sending a test email from Django shell shows up in MailHog UI

### US-3: Transactional Email — Class Invitations

**As a** guardian, **I want** to receive an email when I'm invited to a class, **so that** I can join the class by clicking a link.

**Acceptance Criteria:**

- [ ] When a `ClassInvitation` is created, an email is sent to the invited email address
- [ ] Email contains: class name, inviter name, and a tokenized invitation link
- [ ] Email uses an HTML template with plain-text fallback
- [ ] Email templates live in `templates/emails/`
- [ ] If the invitation email fails to send, the invitation is still created (email is best-effort, logged on failure)

### US-4: Transactional Email — Payment Confirmation

**As a** guardian, **I want** to receive an email when my payment is confirmed or rejected, **so that** I know the status of my contribution.

**Acceptance Criteria:**

- [ ] When a `Payment` status changes to `confirmed`, an email is sent to the guardian's email
- [ ] When a `Payment` status changes to `rejected`, an email is sent with the rejection reason (if provided)
- [ ] Emails include: event name, payment amount, new status, and a link to the event detail page
- [ ] Email uses an HTML template with plain-text fallback

### US-5: Transactional Email — Event Notifications

**As a** guardian, **I want** to receive an email when a new event is created in my class, **so that** I can participate or contribute.

**Acceptance Criteria:**

- [ ] When an `Event` is created, an email is sent to all guardians who are members of the event's class
- [ ] Email includes: event name, description, type (payment/potluck/mixed), date, and a link to the event page
- [ ] Emails are sent asynchronously or in bulk to avoid blocking the request (use Django's `send_mass_mail` or similar)
- [ ] Email uses an HTML template with plain-text fallback

### US-6: Email Service Abstraction

**As a** developer, **I want** a centralized email service, **so that** all transactional emails are sent consistently and are easy to maintain.

**Acceptance Criteria:**

- [ ] An `EmailService` class is created in `apps/core/services/email.py`
- [ ] The service provides methods: `send_invitation_email()`, `send_payment_status_email()`, `send_event_notification_email()`
- [ ] The service is registered in the dependency injection container (`apps/core/containers.py`)
- [ ] All email sending goes through this service (no direct `send_mail` calls in views/models)
- [ ] The service handles errors gracefully (logs failures, does not raise to caller)
- [ ] Base HTML email template with School Hub branding in `templates/emails/base_email.html`

---

## Phase 2 — Production Deployment

### US-7: Fly.io Deployment Configuration

**As a** devops engineer, **I want** to deploy School Hub to Fly.io, **so that** the application is accessible on the internet.

**Acceptance Criteria:**

- [ ] `fly.toml` created with app configuration (region, VM size, port mapping, health checks)
- [ ] Dockerfile production stage works with Fly.io (exposes port 8000, Gunicorn)
- [ ] Fly.io secrets configured for: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, and all service credentials
- [ ] Health check endpoint available (e.g., `/health/` returning 200)
- [ ] `fly deploy` succeeds and the app is accessible
- [ ] Production settings (`config/settings/prod.py`) updated with Fly.io-specific config
- [ ] `.dockerignore` updated to exclude dev files, `.git`, `media/`, `__pycache__`, etc.

### US-8: Supabase PostgreSQL Integration

**As a** devops engineer, **I want** to use Supabase PostgreSQL as the production database, **so that** I have a managed, scalable database.

**Acceptance Criteria:**

- [ ] Production `DATABASE_URL` points to Supabase PostgreSQL connection string
- [ ] SSL mode is required for the connection (`sslmode=require` in the URL or Django settings)
- [ ] Connection pooling is configured appropriately for Fly.io (Supabase provides PgBouncer)
- [ ] Migrations run successfully against Supabase (`fly ssh console -C "python manage.py migrate"`)
- [ ] `CONN_MAX_AGE` and pool settings tuned for serverless/container environment

### US-9: Cloudflare R2 Production Storage

**As a** devops engineer, **I want** to use Cloudflare R2 for file storage in production, **so that** receipt uploads are stored reliably and cheaply.

**Acceptance Criteria:**

- [ ] Production settings configure `django-storages` S3 backend pointing to Cloudflare R2
- [ ] R2 bucket created and configured with appropriate CORS policy for the application domain
- [ ] Environment variables: `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_BUCKET_NAME`, `STORAGE_ENDPOINT_URL` (R2 endpoint)
- [ ] S3v4 signature version configured in Django settings (required by R2)
- [ ] File uploads from production app land in R2 bucket
- [ ] Media files served via R2 public URL or presigned URLs
- [ ] `DEFAULT_FILE_STORAGE` set in prod settings

### US-10: Resend Email Provider

**As a** devops engineer, **I want** to use Resend as the production email provider, **so that** transactional emails are delivered reliably.

**Acceptance Criteria:**

- [ ] Production settings configure Django SMTP backend with Resend SMTP credentials
- [ ] Environment variables: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- [ ] Resend SMTP settings: `smtp.resend.com`, port `465` (SSL) or `587` (TLS), API key as password
- [ ] `DEFAULT_FROM_EMAIL` set to a verified sender domain (e.g., `noreply@schoolhub.com`)
- [ ] All transactional emails (invitations, payment status, event notifications) send successfully via Resend
- [ ] Email delivery is verified end-to-end in production

### US-11: Production Settings Hardening

**As a** devops engineer, **I want** production settings to be secure and complete, **so that** the deployed application is safe.

**Acceptance Criteria:**

- [ ] `SECRET_KEY` loaded from environment variable (no default in prod)
- [ ] `DEBUG = False` enforced
- [ ] `ALLOWED_HOSTS` configured from environment variable
- [ ] `CSRF_TRUSTED_ORIGINS` set for the Fly.io app domain
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS` set with `SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SECURE_HSTS_PRELOAD`
- [ ] Sentry DSN configured from environment variable (optional, graceful if absent)
- [ ] `CONN_HEALTH_CHECKS = True` for database

---

## Environment Variable Summary

| Variable | Dev (default) | Production |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | `config.settings.prod` |
| `SECRET_KEY` | dev default | **required** |
| `DEBUG` | `True` | `False` |
| `DATABASE_URL` | `postgres://school_hub:school_hub@localhost:5432/school_hub` | Supabase connection string |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Fly.io app domain |
| `STORAGE_ACCESS_KEY` | `minioadmin` | R2 access key |
| `STORAGE_SECRET_KEY` | `minioadmin` | R2 secret key |
| `STORAGE_BUCKET_NAME` | `school-hub-media` | R2 bucket name |
| `STORAGE_ENDPOINT_URL` | `http://localhost:9000` | `https://<account>.r2.cloudflarestorage.com` |
| `EMAIL_HOST` | `localhost` | `smtp.resend.com` |
| `EMAIL_PORT` | `1025` | `587` |
| `EMAIL_HOST_USER` | (empty) | `resend` |
| `EMAIL_HOST_PASSWORD` | (empty) | Resend API key |
| `DEFAULT_FROM_EMAIL` | `noreply@localhost` | `noreply@<domain>` |
| `SENTRY_DSN` | (empty) | Sentry project DSN |

---

## Implementation Order

```
Phase 1 (Local Dev)
  1. US-1  MinIO storage + django-storages migration
  2. US-2  MailHog local email
  3. US-6  Email service abstraction
  4. US-3  Invitation emails
  5. US-4  Payment status emails
  6. US-5  Event notification emails

Phase 2 (Production)
  7. US-11 Production settings hardening
  8. US-9  Cloudflare R2 storage
  9. US-10 Resend email provider
  10. US-8  Supabase PostgreSQL
  11. US-7  Fly.io deployment
```

---

## Technical Notes

- **django-storages** uses the same `S3Boto3Storage` backend for MinIO, R2, and AWS S3 — only the endpoint URL and credentials differ.
- **MailHog** vs **Maildev**: PRD specifies MailHog (`mailhog/mailhog`) as it's more widely used, but Maildev (`maildev/maildev`) is a drop-in alternative if preferred.
- **Resend** supports standard SMTP, so no custom Django backend is needed — the built-in `django.core.mail.backends.smtp.EmailBackend` works.
- **Cloudflare R2** is S3-compatible but requires S3v4 signature and does not support all S3 features (e.g., ACLs). Set `default_acl = None` in the storage config.
- **Fly.io** runs Docker containers. The existing `Dockerfile` is compatible; only `fly.toml` and secrets management are needed.
- **Supabase** provides a standard PostgreSQL connection string with optional connection pooling via PgBouncer (port 6543 for pooled, 5432 for direct).
