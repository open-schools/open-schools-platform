from rest_framework.permissions import BasePermission
from open_schools_platform.marketplace_management.models import OAuth2Token

class HasOAuthScope(BasePermission):
    """
    Проверяет, что у OAuth2 токена (если запрос авторизован через него)
    есть необходимый scope.
    """

    def __init__(self, required_scope: str):
        self.required_scope = required_scope

    def has_permission(self, request, view):
        # Если запрос не авторизован через OAuth2Token, пропускаем (возможно это обычный JWT)
        # Если вы хотите, чтобы эндпоинт был доступен ТОЛЬКО для OAuth, нужно изменить логику
        if not request.auth or not isinstance(request.auth, OAuth2Token):
            # Переход к другим разрешениям, если токен не OAuth2
            # Здесь мы просто позволяем запросу перейти к другим классам разрешений
            return True

        granted_scopes = request.auth.scope.split()
        if self.required_scope not in granted_scopes:
            return False

        # Контекстная проверка для конкретной организации
        org_id = None
        if hasattr(view, 'kwargs') and 'organization_id' in view.kwargs:
            org_id = view.kwargs['organization_id']
        elif 'organization' in request.GET:
            org_id = request.GET['organization']

        if org_id:
            from open_schools_platform.marketplace_management.models import Installation
            inst = Installation.objects.filter(
                app=request.auth.app,
                organization_id=org_id,
                active=True,
                deleted__isnull=True
            ).first()
            if not inst or self.required_scope not in inst.granted_scopes.split():
                return False

        return True

    def __call__(self, *args, **kwargs):
        # Позволяет передавать аргументы в класс разрешений
        return self
