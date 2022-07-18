from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_not_logged_in_user


class UserEditingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_change_name_url = reverse("api:user-management:authentication:me:info")
        self.user_update_password_url = reverse("api:user-management:authentication:me:update-password")
        self.jwt_login_url = reverse('api:user-management:authentication:jwt:login')

    def test_name_successfully_changed(self):
        create_logged_in_user(instance=self)
        data = {
            "name": "test_user_changed_name"
        }

        response = self.client.put(self.user_change_name_url, data)
        self.assertEqual(200, response.status_code)
        user = get_user(filters={"phone": "+79025456481"})
        self.assertEqual("test_user_changed_name", user.name)

    def test_user_successfully_changed_password(self):
        create_logged_in_user(instance=self)
        data = {
            "old_password": "123456",
            "new_password": "654321"
        }

        response = self.client.put(self.user_update_password_url, data)
        self.assertEqual(200, response.status_code)
        user = get_user(filters={"phone": "+79025456481"})
        self.assertTrue(user.check_password("654321"))

    def test_old_password_does_not_match_with_actual_one(self):
        create_logged_in_user(instance=self)
        data = {
            "old_password": "000000",
            "new_password": "123456"
        }

        response = self.client.put(self.user_update_password_url, data)
        self.assertEqual(401, response.status_code)

    def test_old_password_match_with_new_one(self):
        create_logged_in_user(instance=self)
        data = {
            "old_password": "654321",
            "new_password": "654321"
        }

        response = self.client.put(self.user_update_password_url, data)
        self.assertEqual(401, response.status_code)

    def test_request_user_is_not_logged_in(self):
        create_not_logged_in_user()
        data_for_name_change = {
            "name": "Alex"
        }
        data_for_password_update = {
            "old_password": "111111",
            "new_password": "222222"
        }
        response_for_name_change = self.client.put(self.user_change_name_url, data_for_name_change)
        self.assertEqual(401, response_for_name_change.status_code)
        response_for_password_update = self.client.put(self.user_update_password_url, data_for_password_update)
        self.assertEqual(401, response_for_password_update.status_code)
