"""
URL configuration for School Hub project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Apps
    path("", include("apps.core.urls", namespace="site")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("classes/", include("apps.classes.urls", namespace="classes")),
    path("events/", include("apps.events.urls", namespace="events")),
    path("suppliers/", include("apps.suppliers.urls", namespace="suppliers")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

    # Debug toolbar
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
