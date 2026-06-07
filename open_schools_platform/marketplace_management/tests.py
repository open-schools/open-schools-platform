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
            "client_secret": "test_super_secret",
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
            "client_secret": "test_super_secret",
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
            "client_secret": "test_super_secret",
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
            "client_secret": "test_super_secret",
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
            "client_secret": "test_super_secret"
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
            "client_secret": "test_super_secret",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(res.status_code, 200)
        access_token = res.data["access_token"]
        
        revoke_url = reverse("api:marketplace-management:marketplace:oauth2-revoke")
        revoke_res = self.client.post(revoke_url, {
            "token": access_token,
            "client_id": str(self.app.client_id),
            "client_secret": "test_super_secret"
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
            "client_secret": "test_super_secret",
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
            "client_secret": "test_super_secret",
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

class JiraWebhookTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:marketplace-management:marketplace:webhook-jira-publish-app")
        self.secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', 'test_secret_for_jira_webhooks')
        
    def test_publish_app_with_valid_secret(self):
        payload = {
            "name": "Test App from Jira",
            "description": "Test description",
            "redirect_uris": ["http://localhost/callback"]
        }
        
        response = self.client.post(
            self.url,
            payload,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("client_id", response.data)
        self.assertIn("client_secret", response.data)
        
        # Check if App was created
        self.assertTrue(App.objects.filter(name="Test App from Jira", status=AppStatus.PUBLISHED).exists())
        
    def test_publish_app_with_invalid_secret(self):
        payload = {
            "name": "Hacked App",
            "description": "Hack"
        }
        
        response = self.client.post(
            self.url,
            payload,
            format='json',
            HTTP_AUTHORIZATION="Bearer WRONG_SECRET"
        )
        
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
        # Using reverse with namespace according to current setup
        url = reverse("api:marketplace-management:marketplace:miniapps-reviews", kwargs={"app_id": self.app.id})
        response = self.client.post(url, {
            "rating": 5,
            "message": "Great app!"
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
        
        response = self.client.post(url, {
            "rating": 4,
            "message": "Good app!"
        })
        self.assertEqual(response.status_code, 201)
        
        self.app.refresh_from_db()
        self.assertEqual(self.app.reviews_count, 1)
        self.assertEqual(self.app.average_rating, 4.0)

        response2 = self.client.post(url, {
            "rating": 2,
            "message": "Actually bad."
        })
        self.assertEqual(response2.status_code, 400)


class JiraUpdateDeleteWebhookTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', 'test_secret_for_jira_webhooks')
        
        self.app = App.objects.create(
            name="Original Name",
            description="Original Description",
            client_secret="test_secret"
        )
        self.client_id = str(self.app.client_id)
        
    def test_validate_credentials_success(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-validate-credentials")
        response = self.client.post(
            url,
            {"client_id": self.client_id, "client_secret": "test_secret"},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 200)

    def test_validate_credentials_invalid_secret(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-validate-credentials")
        response = self.client.post(
            url,
            {"client_id": self.client_id, "client_secret": "wrong_secret"},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 403)

    def test_update_app_success(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-update-app")
        response = self.client.post(
            url,
            {
                "client_id": self.client_id,
                "name": "Updated Name",
                "description": "Updated Description"
            },
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 200)
        self.app.refresh_from_db()
        self.assertEqual(self.app.name, "Updated Name")
        self.assertEqual(self.app.description, "Updated Description")

    def test_delete_app_success(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-delete-app")
        response = self.client.post(
            url,
            {"client_id": self.client_id},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(App.objects.filter(client_id=self.client_id).exists())
        self.assertTrue(App.objects.all_with_deleted().filter(client_id=self.client_id).exists())

    def test_regenerate_secret_success(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-regenerate-secret")
        old_hashed_secret = self.app.client_secret
        response = self.client.post(
            url,
            {"client_id": self.client_id},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("client_secret", response.data)
        
        self.app.refresh_from_db()
        self.assertNotEqual(self.app.client_secret, old_hashed_secret)

    def test_restore_app_success(self):
        self.app.delete()
        self.assertFalse(App.objects.filter(client_id=self.client_id).exists())
        
        url = reverse("api:marketplace-management:marketplace:webhook-jira-restore-app")
        response = self.client.post(
            url,
            {"client_id": self.client_id},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {self.secret}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(App.objects.filter(client_id=self.client_id).exists())

import uuid
from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from open_schools_platform.user_management.users.models import User
from open_schools_platform.marketplace_management.models import App, Category, Installation, OAuth2Token, OAuth2AuthorizationCode
from unittest.mock import patch

import uuid
from django.urls import reverse
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient
from open_schools_platform.user_management.users.models import User
from open_schools_platform.marketplace_management.models import App, Category, Installation, OAuth2Token, OAuth2AuthorizationCode
from unittest.mock import patch

class MarketplaceViewsCoverageTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79000000000")
        self.category = Category.objects.create(name="Test Category")
        self.app = App.objects.create(name="Test App", description="Desc")
        self.app.category = self.category
        from open_schools_platform.marketplace_management.models import AppStatus
        self.app.status = AppStatus.PUBLISHED
        self.app.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_app_api_list(self):
        url = reverse("api:marketplace-management:marketplace:miniapps-apps-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_app_api_retrieve(self):
        url = reverse("api:marketplace-management:marketplace:miniapps-apps-detail", kwargs={"pk": self.app.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_api_list(self):
        url = reverse("api:marketplace-management:marketplace:miniapps-categories-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_api_retrieve(self):
        url = reverse("api:marketplace-management:marketplace:miniapps-categories-detail", kwargs={"pk": self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_installation_view_set(self):
        from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee
        from open_schools_platform.organization_management.organizations.models import Organization
        profile = EmployeeProfile.objects.create(user=self.user, name="emp user")
        org = Organization.objects.create(name="emp org")
        Employee.objects.create(employee_profile=profile, organization=org, name="emp")

        install_url = reverse("api:marketplace-management:marketplace:miniapps-installations-list")
        
        response = self.client.post(install_url, {
            "app": str(self.app.id),
            "organization": str(org.id)
        }, format="json")
        self.assertEqual(response.status_code, 201)
        install_id = Installation.objects.last().id
        
        del_url = reverse("api:marketplace-management:marketplace:miniapps-installations-detail", kwargs={"pk": install_id})
        res2 = self.client.delete(del_url)
        self.assertEqual(res2.status_code, 204)

        res3 = self.client.post(install_url, {
            "app": str(self.app.id),
            "organization": str(org.id)
        }, format="json")
        self.assertEqual(res3.status_code, 201)

    def test_installations_view_set_unauthenticated(self):
        unauth_client = APIClient()
        url = reverse("api:marketplace-management:marketplace:miniapps-installations-list")
        response = unauth_client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_admin_installation_view_set_employee(self):
        from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee
        from open_schools_platform.organization_management.organizations.models import Organization
        
        profile = EmployeeProfile.objects.create(user=self.user, name="emp user")
        org = Organization.objects.create(name="emp org")
        Employee.objects.create(employee_profile=profile, organization=org, name="emp")
        Installation.objects.create(app=self.app, organization=org, active=True, user=self.user)
        
        url = reverse("api:marketplace-management:marketplace:admin-installations-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

class OAuth2FlowCoverageTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79000000001")
        self.app = App.objects.create(name="Test App")
        self.client = APIClient()
        
    def test_oauth2_authorization_code_not_found(self):
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": "invalid_code_str",
            "client_id": self.app.client_id,
            "client_secret": "plain_secret",
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or expired authorization code", str(response.data))

    def test_oauth2_unsupported_code_challenge_method(self):
        code = OAuth2AuthorizationCode.objects.create(
            code="test_unsupported",
            user=self.user,
            app=self.app,
            redirect_uri="http://localhost/callback",
            response_type="code",
            code_challenge="test",
            code_challenge_method="test"
        )
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": "test_unsupported",
            "client_id": self.app.client_id,
            "client_secret": "plain_secret",
            "code_verifier": "test",
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Unsupported code_challenge_method", str(response.data))

    def test_oauth2_invalid_code_verifier_s256(self):
        code = OAuth2AuthorizationCode.objects.create(
            code="test_s256_invalid",
            user=self.user,
            app=self.app,
            redirect_uri="http://localhost/callback",
            response_type="code",
            code_challenge="test",
            code_challenge_method="S256"
        )
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": "test_s256_invalid",
            "client_id": self.app.client_id,
            "client_secret": "plain_secret",
            "code_verifier": "invalid",
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid code_verifier", str(response.data))

    def test_oauth2_plain_secret_mismatch(self):
        code = OAuth2AuthorizationCode.objects.create(
            code="test_plain_secret",
            user=self.user,
            app=self.app,
            redirect_uri="http://localhost/callback",
            response_type="code"
        )
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": "test_plain_secret",
            "client_id": self.app.client_id,
            "client_secret": "invalid_plain",
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid client_secret", str(response.data))

    def test_oauth2_refresh_token_plain_secret_mismatch(self):
        token = OAuth2Token.objects.create(
            user=self.user,
            app=self.app,
            access_token="acc123",
            refresh_token="ref123",
            expires_in=3600
        )
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "refresh_token",
            "refresh_token": "ref123",
            "client_id": self.app.client_id,
            "client_secret": "invalid_plain"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid client_secret", str(response.data))

    def test_revoke_token_plain_secret_mismatch(self):
        token = OAuth2Token.objects.create(
            user=self.user,
            app=self.app,
            access_token="acc123",
            refresh_token="ref123",
            expires_in=3600
        )
        url = reverse("api:marketplace-management:marketplace:oauth2-revoke")
        response = self.client.post(url, {
            "token": "acc123",
            "client_id": self.app.client_id,
            "client_secret": "invalid_plain"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid client_secret", str(response.data))

    def test_revoke_token_app_not_found(self):
        url = reverse("api:marketplace-management:marketplace:oauth2-revoke")
        response = self.client.post(url, {
            "token": "acc123",
            "client_id": str(uuid.uuid4()),
            "client_secret": "secret"
        })
        self.assertEqual(response.status_code, 200)

class JiraUpdateDeleteWebhookTestsRecovered(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(phone="+79000000002")
        self.app = App.objects.create(name="Test App")
        self.client = APIClient()

    @override_settings(JIRA_WEBHOOK_SECRET='test_secret')
    def test_webhook_jira_regenerate_secret_invalid_signature(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-regenerate-secret")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 403)

    @override_settings(JIRA_WEBHOOK_SECRET='test_secret')
    def test_webhook_jira_regenerate_secret_valid(self):
        old_secret = self.app.client_secret
        url = reverse("api:marketplace-management:marketplace:webhook-jira-regenerate-secret")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_secret')
        response = self.client.post(url, {"client_id": str(self.app.client_id)}, format="json")
        self.assertEqual(response.status_code, 200)
        self.app.refresh_from_db()
        self.assertNotEqual(self.app.client_secret, old_secret)

    @override_settings(JIRA_WEBHOOK_SECRET='test_secret')
    def test_webhook_jira_restore_app_invalid_signature(self):
        url = reverse("api:marketplace-management:marketplace:webhook-jira-restore-app")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 403)

    @override_settings(JIRA_WEBHOOK_SECRET='test_secret')
    def test_webhook_jira_restore_app_valid(self):
        self.app.delete()
        self.assertTrue(App.all_objects.get(id=self.app.id).deleted is not None)
        url = reverse("api:marketplace-management:marketplace:webhook-jira-restore-app")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test_secret')
        response = self.client.post(url, {"client_id": str(self.app.client_id)}, format="json")
        self.assertEqual(response.status_code, 200)
        app = App.objects.get(id=self.app.id)
        self.assertFalse(app.deleted)

