import logging

from django.urls import re_path

logger = logging.getLogger("configuration")


def show_swagger_api(*args, **kwargs) -> bool:

    from .settings import SWAGGER_ENABLED

    if not SWAGGER_ENABLED:
        return False
    try:
        import drf_yasg  # noqa
    except ImportError:
        logger.info("No installation found for: swagger")
        return False

    return True


class SwaggerSetup:
    """
    We use a class, just for namespacing convenience.
    """

    @staticmethod
    def do_settings(INSTALLED_APPS, MIDDLEWARE, middleware_position=None):
        _show_swagger_api: bool = show_swagger_api()
        logger.info(f"Swagger in use: {_show_swagger_api}")

        if not _show_swagger_api:
            return INSTALLED_APPS, MIDDLEWARE

        INSTALLED_APPS = INSTALLED_APPS + ["drf_yasg"]

        return INSTALLED_APPS, MIDDLEWARE

    @staticmethod
    def do_urls(urlpatterns):
        if not show_swagger_api():
            return urlpatterns

        from rest_framework import permissions
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi

        schema_view = get_schema_view(
            openapi.Info(
                title="Open Schools Platform API",
                default_version='v1',
                description="Backend for open source schools management platform",
                contact=openapi.Contact(email="inbox@lamart.site"),
                license=openapi.License(name="MIT License"),
            ),
            public=True,
            permission_classes=[permissions.AllowAny],
        )

        return urlpatterns + [
            re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
            re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        ]
