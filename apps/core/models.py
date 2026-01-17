"""
Base models for the School Hub project.
Provides abstract base classes with common fields and behaviors.
"""

import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    created_at and updated_at fields.
    """

    created_at = models.DateTimeField(
        "Criado em",
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        "Atualizado em",
        auto_now=True,
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that provides a UUID primary key.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Abstract base model combining UUID and timestamp functionality.
    This is the recommended base class for most models.
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_deleted(self):
        """Return all objects including soft-deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft-deleted objects."""
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    Records are marked as deleted but not removed from the database.
    """

    deleted_at = models.DateTimeField(
        "Excluído em",
        null=True,
        blank=True,
        editable=False,
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the record."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the record."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None
