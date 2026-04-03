"""
Base settings for School Hub project.
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="", cast=Csv())

# Application definition
DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "widget_tweaks",
    "crispy_forms",
    "crispy_tailwind",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.classes",
    "apps.events",
    "apps.suppliers",
    "apps.dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL", default="postgres://school_hub:school_hub@localhost:5432/school_hub"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Login URLs
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "site:home"

# Unfold Admin Settings
UNFOLD = {
    "SITE_TITLE": "School Hub",
    "SITE_HEADER": "School Hub",
    "SITE_SUBHEADER": "Gestão de Eventos Escolares",
    "SITE_SYMBOL": "school",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "config.settings.base.environment_callback",
    "DASHBOARD_CALLBACK": "apps.dashboard.views.dashboard_callback",
    "STYLES": [],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navegação",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                ],
            },
            {
                "title": "Gestão",
                "separator": True,
                "items": [
                    {
                        "title": "Turmas",
                        "icon": "groups",
                        "link": lambda request: "/admin/classes/schoolclass/",
                    },
                    {
                        "title": "Eventos",
                        "icon": "event",
                        "link": lambda request: "/admin/events/event/",
                    },
                    {
                        "title": "Pagamentos",
                        "icon": "payments",
                        "link": lambda request: "/admin/events/payment/",
                    },
                ],
            },
            {
                "title": "Cadastros",
                "separator": True,
                "items": [
                    {
                        "title": "Responsáveis",
                        "icon": "person",
                        "link": lambda request: "/admin/accounts/guardian/",
                    },
                    {
                        "title": "Alunos",
                        "icon": "child_care",
                        "link": lambda request: "/admin/classes/student/",
                    },
                    {
                        "title": "Fornecedores",
                        "icon": "store",
                        "link": lambda request: "/admin/suppliers/supplier/",
                    },
                ],
            },
            {
                "title": "Sistema",
                "separator": True,
                "items": [
                    {
                        "title": "Usuários",
                        "icon": "manage_accounts",
                        "link": lambda request: "/admin/accounts/user/",
                    },
                ],
            },
        ],
    },
}


# Storage (S3-compatible: MinIO in dev, Cloudflare R2 in prod)
STORAGE_ACCESS_KEY = config("STORAGE_ACCESS_KEY", default="minioadmin")
STORAGE_SECRET_KEY = config("STORAGE_SECRET_KEY", default="minioadmin")
STORAGE_BUCKET_NAME = config("STORAGE_BUCKET_NAME", default="school-hub-media")
STORAGE_ENDPOINT_URL = config("STORAGE_ENDPOINT_URL", default="http://localhost:9000")
STORAGE_CUSTOM_DOMAIN = config("STORAGE_CUSTOM_DOMAIN", default="")

# Email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=1025, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@localhost")


def environment_callback(request) -> tuple[str, str]:
    """Return environment name and color for Unfold admin."""
    if DEBUG:
        return "Desenvolvimento", "warning"
    return "Produção", "success"
