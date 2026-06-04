from django.test import TransactionTestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.marketplace_management.models import App, Installation, OAuth2AuthorizationCode, OAuth2Token, AppStatus
from open_schools_platform.user_management.users.models import User
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee
import secrets
import base64
import hashlib

def generate_pkce():
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')
    return verifier, challenge

class OAuth2FlowTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone="+79001234567", password="testpassword")
        
        # Using objects.create instead of create_employee_profile if method signature differs
        self.profile = EmployeeProfile.objects.create(user=self.user, name="Test User")
        self.org = Organization.objects.create(name="Test Org")
        self.employee = Employee.objects.create(employee_profile=self.profile, organization=self.org, name="Test User")
        
        self.app = App.objects.create(
            name="Test App", 
            redirect_uris=["http://localhost/callback"],
            client_secret="test_super_secret"
        )
        
        self.installation = Installation.objects.create(
            app=self.app,
            organization=self.org,
            user=self.user,
            active=True,
            granted_scopes="openid profile email phone"
        )

    def test_authorize_redirects_with_code_when_installed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("api:marketplace-management:marketplace:oauth2-authorize")
        verifier, challenge = generate_pkce()
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("http://localhost/callback?code="))
        
        # Verify code was created
        code_str = response.url.split("code=")[1]
        self.assertTrue(OAuth2AuthorizationCode.objects.filter(code=code_str).exists())

    def test_authorize_fails_when_not_installed(self):
        self.installation.delete()
        self.client.force_authenticate(user=self.user)
        url = reverse("api:marketplace-management:marketplace:oauth2-authorize")
        verifier, challenge = generate_pkce()
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("error=access_denied", response.url)

    def test_token_exchange(self):
        verifier, challenge = generate_pkce()
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", code_challenge=challenge)
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        
        if response.status_code != 200:
            print(f"DEBUG: {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.data)
        
        # Code should be deleted
        self.assertFalse(OAuth2AuthorizationCode.objects.filter(code=auth_code.code).exists())
        
        # Token should be created
        self.assertTrue(OAuth2Token.objects.filter(access_token=response.data["access_token"]).exists())

    def test_userinfo_endpoint(self):
        verifier, challenge = generate_pkce()
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", scope="openid profile email phone", code_challenge=challenge)
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        
        access_token = res.data["access_token"]
        
        userinfo_url = reverse("api:marketplace-management:marketplace:oauth2-userinfo")
        response = self.client.get(userinfo_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["phone"], str(self.user.phone))
        self.assertEqual(response.data["name"], self.profile.name)

    def test_token_exchange_invalid_secret(self):
        verifier, challenge = generate_pkce()
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", code_challenge=challenge)
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": "wrong_secret",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        
        self.assertEqual(response.status_code, 403)
        self.assertFalse(App.objects.filter(name="Hacked App").exists())


class ReviewTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone="+79009998877", password="testpassword")
        self.profile = EmployeeProfile.objects.create(user=self.user, name="Review User")
        self.org = Organization.objects.create(name="Review Org")
        self.employee = Employee.objects.create(employee_profile=self.profile, organization=self.org, name="Review User")
        
        from open_schools_platform.marketplace_management.models import AppStatus
        self.app = App.objects.create(
            name="Review App", 
            status=AppStatus.PUBLISHED
        )

    def test_create_review_without_installation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("api:marketplace-management:marketplace:oauth2-authorize")
        verifier, challenge = generate_pkce()
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback",
            "scope": "openid profile",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })
        self.assertEqual(response.status_code, 403)

    def test_create_review_with_installation(self):
        Installation.objects.create(
            app=self.app,
            organization=self.org,
            user=self.user,
            active=True
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("api:marketplace-management:marketplace:miniapps-reviews", kwargs={"app_id": self.app.id})
        
        from open_schools_platform.marketplace_management.models import OAuth2AuthorizationCode
        auth_code = OAuth2AuthorizationCode.objects.get(code=code_str)
        self.assertEqual(auth_code.scope, "openid profile")
        
        # Now exchange
        token_url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(token_url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 201)
        
        self.assertEqual(res.status_code, 200)
        from open_schools_platform.marketplace_management.models import OAuth2Token
        token = OAuth2Token.objects.get(access_token=res.data["access_token"])
        self.assertEqual(token.scope, "openid profile")

    def test_refresh_token_exchange(self):
        verifier, challenge = generate_pkce()
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", scope="openid profile", code_challenge=challenge)
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(res.status_code, 200)
        refresh_token = res.data["refresh_token"]
        old_access_token = res.data["access_token"]
        
        res = self.client.post(url, {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("access_token", res.data)
        self.assertNotEqual(res.data["access_token"], old_access_token)
        
    def test_revoke_token(self):
        verifier, challenge = generate_pkce()
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", code_challenge=challenge)
        
        token_url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(token_url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(res.status_code, 200)
        access_token = res.data["access_token"]
        
        revoke_url = reverse("api:marketplace-management:marketplace:oauth2-revoke")
        revoke_res = self.client.post(revoke_url, {
            "token": access_token,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret
        })
        self.assertEqual(revoke_res.status_code, 200)
        
        from open_schools_platform.marketplace_management.models import OAuth2Token
        token_obj = OAuth2Token.objects.get(access_token=access_token)
        self.assertTrue(token_obj.revoked)
        
        # Now try to use the revoked token
        userinfo_url = reverse("api:marketplace-management:marketplace:oauth2-userinfo")
        info_res = self.client.get(userinfo_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.assertEqual(info_res.status_code, 403)

    def test_authorization_code_expires(self):
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        from datetime import timedelta
        from django.utils import timezone
        
        verifier, challenge = generate_pkce()
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", code_challenge=challenge)
        
        # Manually set auth_time to 6 minutes ago
        auth_code.auth_time = timezone.now() - timedelta(minutes=6)
        auth_code.save()
        
        token_url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(token_url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        
        # Should fail with 400 because code is expired
        self.assertEqual(res.status_code, 400)
        
    def test_access_token_expires(self):
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        from datetime import timedelta
        from django.utils import timezone
        
        verifier, challenge = generate_pkce()
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback", scope="openid profile", code_challenge=challenge)
        
        token_url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(token_url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret,
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(res.status_code, 200)
        access_token = res.data["access_token"]
        
        # Manually set created_at of token to 2 hours ago
        token_obj = OAuth2Token.objects.get(access_token=access_token)
        token_obj.created_at = timezone.now() - timedelta(hours=2)
        token_obj.save()
        
        userinfo_url = reverse("api:marketplace-management:marketplace:oauth2-userinfo")
        info_res = self.client.get(userinfo_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        # Should fail with 403 because token is expired
        self.assertEqual(info_res.status_code, 403)
