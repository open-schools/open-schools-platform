import secrets
from django.utils import timezone
from open_schools_platform.marketplace_management.models import OAuth2AuthorizationCode, OAuth2Token, App, Installation
from open_schools_platform.user_management.users.models import User
from open_schools_platform.errors.exceptions import InvalidArgument


def create_authorization_code(app: App, user: User, redirect_uri: str, scope: str = "") -> OAuth2AuthorizationCode:
    code_str = secrets.token_urlsafe(32)
    auth_code = OAuth2AuthorizationCode.objects.create(
        code=code_str,
        user=user,
        app=app,
        redirect_uri=redirect_uri,
        response_type="code",
        scope=scope
    )
    return auth_code


def exchange_code_for_token(code_str: str, client_id: str) -> dict:
    try:
        auth_code = OAuth2AuthorizationCode.objects.get(code=code_str, app__client_id=client_id)
    except OAuth2AuthorizationCode.DoesNotExist:
        raise InvalidArgument("Invalid or expired authorization code")

    # Generate tokens
    access_token = secrets.token_urlsafe(64)
    refresh_token = secrets.token_urlsafe(64)
    expires_in = 3600  # 1 hour

    token = OAuth2Token.objects.create(
        user=auth_code.user,
        app=auth_code.app,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=expires_in
    )

    # Invalidate code
    auth_code.delete()

    return {
        "access_token": token.access_token,
        "token_type": "Bearer",
        "expires_in": token.expires_in,
        "refresh_token": token.refresh_token
    }


def check_installation_exists(user: User, app: App) -> bool:
    # Is the app installed specifically for this user?
    if Installation.objects.filter(app=app, user=user, active=True).exists():
        return True

    # Is the app installed by any organization the user belongs to?
    if Installation.objects.filter(
        app=app,
        organization__employees__employee_profile__user=user,
        active=True
    ).exists():
        return True

    return False
