import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class TeacherExceptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_teacher_profile_url = \
            lambda pk: reverse("api:organization-management:teachers:get-teacher-profile", args=[pk])

    def test_get_teacher_profile_does_not_exist(self):
        create_logged_in_user(self)
        response = self.client.get(self.get_teacher_profile_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_get_teacher_profile_wrong_access(self):
        create_logged_in_user(self)
        response = self.client.get(self.get_teacher_profile_url(
            pk=str(create_test_user("+79020000000").teacher_profile.pk))
        )
        self.assertEqual(403, response.status_code)
