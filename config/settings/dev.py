"""
Development settings for School Hub project.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Development apps
INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE  # noqa: F405

# Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

# Email — SMTP backend pointing to MailHog
# EMAIL_HOST / EMAIL_PORT are read from base.py via env vars (default: localhost:1025)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# File storage — S3Boto3 pointing to MinIO
_storage_options: dict = {
    "access_key": STORAGE_ACCESS_KEY,  # noqa: F405
    "secret_key": STORAGE_SECRET_KEY,  # noqa: F405
    "bucket_name": STORAGE_BUCKET_NAME,  # noqa: F405
    "endpoint_url": STORAGE_ENDPOINT_URL,  # noqa: F405
    "use_ssl": False,
    "url_protocol": "http:",
    "addressing_style": "path",
    "signature_version": "s3v4",
    "default_acl": None,
    "file_overwrite": False,
    "querystring_auth": False,
}
if STORAGE_CUSTOM_DOMAIN:  # noqa: F405
    _storage_options["custom_domain"] = STORAGE_CUSTOM_DOMAIN  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": _storage_options,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
