from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from open_schools_platform.marketplace_management.models import OAuth2Token

class OAuth2TokenAuthentication(BaseAuthentication):
    """
    Аутентификация с использованием OAuth2 токена, выпущенного нашей платформой
    для мини-приложений (Marketplace).
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token_str = auth_header.split(' ')[1]
        
        try:
            token = OAuth2Token.objects.select_related('user').get(access_token=token_str, revoked=False)
        except OAuth2Token.DoesNotExist:
            return None

        # You can also add token expiration check here if expires_in is implemented
        # Currently, logic assumes revoked=False is enough, but consider time check if needed.

        return (token.user, token)
