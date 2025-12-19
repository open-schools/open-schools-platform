from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.marketplace_management.models import App

@selector_factory(App)
def get_app(*, filters=None, user=None, prefetch_related_list=None) -> App:
    from open_schools_platform.marketplace_management.filters import AppFilterset  # чтобы избежать циклического импорта

    filters = filters or {}

    qs = App.objects.prefetch_related(*prefetch_related_list).all()
    app = AppFilterset(filters, qs).qs.first()

    if user and app and not user.has_perm("marketplace_management.app_access", app):  # возможно, другое разрешение
        raise PermissionDenied

    return app