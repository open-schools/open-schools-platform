from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class GetTeacherProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_teacher_profile_url = \
            lambda pk: reverse("api:organization-management:teachers:get-teacher-profile", args=[pk])

    def test_successfully_get_teacher_profile_as_his_owner(self):
        user = create_logged_in_user(self)
        response = self.client.get(self.get_teacher_profile_url(pk=str(user.teacher_profile.pk)))
        self.assertEqual(200, response.status_code)
