"""
Dependency Injection Containers for School Hub.
Uses dependency-injector for IoC container management.
"""

from dependency_injector import containers, providers

from apps.core.services.pix import PixService, PixServiceInterface


class CoreContainer(containers.DeclarativeContainer):
    """Container for core services."""

    config = providers.Configuration()

    # PIX Service
    pix_service: providers.Provider[PixServiceInterface] = providers.Singleton(
        PixService,
        pix_key=config.pix_key,
        merchant_name=config.pix_merchant_name,
        merchant_city=config.pix_merchant_city,
    )


class AppContainer(containers.DeclarativeContainer):
    """Main application container."""

    config = providers.Configuration()

    # Core container
    core = providers.Container(
        CoreContainer,
        config=config,
    )


# Global container instance
container = AppContainer()


def configure_container():
    """Configure the container with settings."""
    from django.conf import settings

    container.config.from_dict(
        {
            "pix_key": getattr(settings, "PIX_KEY", ""),
            "pix_merchant_name": getattr(settings, "PIX_MERCHANT_NAME", ""),
            "pix_merchant_city": getattr(settings, "PIX_MERCHANT_CITY", ""),
        }
    )
