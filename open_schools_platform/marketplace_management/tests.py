from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.marketplace_management.models import App, Installation, OAuth2AuthorizationCode, OAuth2Token
from open_schools_platform.user_management.users.models import User
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee

class OAuth2FlowTests(TestCase):
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
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback"
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
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback"
        })
        self.assertEqual(response.status_code, 403)

    def test_token_exchange(self):
        # Create a code
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback")
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret
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
        # Exchange for token
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback")
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret
        })
        
        access_token = res.data["access_token"]
        
        userinfo_url = reverse("api:marketplace-management:marketplace:oauth2-userinfo")
        response = self.client.get(userinfo_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["phone"], str(self.user.phone))
        self.assertEqual(response.data["name"], self.profile.name)

    def test_token_exchange_invalid_secret(self):
        from open_schools_platform.marketplace_management.oauth2_services import create_authorization_code
        auth_code = create_authorization_code(self.app, self.user, "http://localhost/callback")
        
        url = reverse("api:marketplace-management:marketplace:oauth2-token")
        response = self.client.post(url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": "wrong_secret"
        })
        
        self.assertEqual(response.status_code, 403)

    def test_authorize_with_scope(self):
        self.installation.granted_scopes = "openid profile"
        self.installation.save()
        
        self.client.force_authenticate(user=self.user)
        url = reverse("api:marketplace-management:marketplace:oauth2-authorize")
        response = self.client.get(url, {
            "client_id": self.app.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost/callback",
            "scope": "openid profile"
        })
        self.assertEqual(response.status_code, 302)
        code_str = response.url.split("code=")[1]
        
        from open_schools_platform.marketplace_management.models import OAuth2AuthorizationCode
        auth_code = OAuth2AuthorizationCode.objects.get(code=code_str)
        self.assertEqual(auth_code.scope, "openid profile")
        
        # Now exchange
        token_url = reverse("api:marketplace-management:marketplace:oauth2-token")
        res = self.client.post(token_url, {
            "grant_type": "authorization_code",
            "code": auth_code.code,
            "client_id": str(self.app.client_id),
            "client_secret": self.app.client_secret
        })
        
        self.assertEqual(res.status_code, 200)
        from open_schools_platform.marketplace_management.models import OAuth2Token
        token = OAuth2Token.objects.get(access_token=res.data["access_token"])
        self.assertEqual(token.scope, "openid profile")
