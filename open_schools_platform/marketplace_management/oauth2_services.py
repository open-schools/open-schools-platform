import secrets
import base64
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from open_schools_platform.marketplace_management.models import OAuth2AuthorizationCode, OAuth2Token, App, Installation
from open_schools_platform.user_management.users.models import User
from open_schools_platform.errors.exceptions import InvalidArgument
from rest_framework.exceptions import PermissionDenied


def create_authorization_code(app: App, user: User, redirect_uri: str, scope: str = "", code_challenge: str = "", code_challenge_method: str = "S256") -> OAuth2AuthorizationCode:
    code_str = secrets.token_urlsafe(32)
    auth_code = OAuth2AuthorizationCode.objects.create(
        code=code_str,
        user=user,
        app=app,
        redirect_uri=redirect_uri,
        response_type="code",
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method
    )
    return auth_code


def exchange_code_for_token(code_str: str, client_id: str, client_secret: str, code_verifier: str = "") -> dict:
    try:
        auth_code = OAuth2AuthorizationCode.objects.get(code=code_str, app__client_id=client_id)
    except OAuth2AuthorizationCode.DoesNotExist:
        raise InvalidArgument("Invalid or expired authorization code")

    if auth_code.auth_time + timedelta(minutes=5) < timezone.now():
        auth_code.delete()
        raise InvalidArgument("Authorization code expired")

    if auth_code.code_challenge:
        if not code_verifier:
            raise InvalidArgument("code_verifier is required")
            
        if auth_code.code_challenge_method == "S256":
            # Hash code_verifier with SHA256 and base64url encode it
            digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
            calculated_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')
            if calculated_challenge != auth_code.code_challenge:
                raise PermissionDenied("Invalid code_verifier")
        elif auth_code.code_challenge_method == "plain":
            if code_verifier != auth_code.code_challenge:
                raise PermissionDenied("Invalid code_verifier")
        else:
            raise PermissionDenied("Unsupported code_challenge_method")

    # If client_secret in DB is hashed, we use check_password. If it's plain text (not yet hashed), we fall back to simple equality
    # This ensures backwards compatibility with unhashed secrets temporarily.
    db_secret = auth_code.app.client_secret
    if db_secret.startswith('pbkdf2_') or db_secret.startswith('bcrypt_'):
        if not check_password(client_secret, db_secret):
            raise PermissionDenied("Invalid client_secret")
    else:
        if db_secret != client_secret:
            raise PermissionDenied("Invalid client_secret")

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
        expires_in=expires_in,
        scope=auth_code.scope
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


def exchange_refresh_token(refresh_token_str: str, client_id: str, client_secret: str) -> dict:
    try:
        old_token = OAuth2Token.objects.get(
            refresh_token=refresh_token_str, 
            app__client_id=client_id, 
            revoked=False
        )
    except OAuth2Token.DoesNotExist:
        raise InvalidArgument("Invalid or revoked refresh token")

    db_secret = old_token.app.client_secret
    if db_secret.startswith('pbkdf2_') or db_secret.startswith('bcrypt_'):
        if not check_password(client_secret, db_secret):
            raise PermissionDenied("Invalid client_secret")
    else:
        if db_secret != client_secret:
            raise PermissionDenied("Invalid client_secret")

    # Revoke old token
    old_token.revoked = True
    old_token.save(update_fields=['revoked'])

    # Generate new tokens
    access_token = secrets.token_urlsafe(64)
    refresh_token = secrets.token_urlsafe(64)
    expires_in = 3600  # 1 hour

    new_token = OAuth2Token.objects.create(
        user=old_token.user,
        app=old_token.app,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=expires_in,
        scope=old_token.scope
    )

    return {
        "access_token": new_token.access_token,
        "token_type": "Bearer",
        "expires_in": new_token.expires_in,
        "refresh_token": new_token.refresh_token
    }


def revoke_token(token_str: str, client_id: str, client_secret: str):
    try:
        app = App.objects.get(client_id=client_id)
        db_secret = app.client_secret
        if db_secret.startswith('pbkdf2_') or db_secret.startswith('bcrypt_'):
            if not check_password(client_secret, db_secret):
                raise PermissionDenied("Invalid client_secret")
        else:
            if db_secret != client_secret:
                raise PermissionDenied("Invalid client_secret")
            
        # Revoke the token by matching access or refresh token
        updated = OAuth2Token.objects.filter(
            app=app,
            access_token=token_str
        ).update(revoked=True)
        
        if not updated:
            OAuth2Token.objects.filter(
                app=app,
                refresh_token=token_str
            ).update(revoked=True)
            
    except App.DoesNotExist:
        pass

