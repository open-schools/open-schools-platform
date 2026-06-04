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
            # Fallback to other permissions if token is not OAuth2
            # Here we just allow it to pass to other permission classes
            return True

        granted_scopes = request.auth.scope.split()
        return self.required_scope in granted_scopes

    def __call__(self, *args, **kwargs):
        # Allow passing arguments to the permission class
        return self
