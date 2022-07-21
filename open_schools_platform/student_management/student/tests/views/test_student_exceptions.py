from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.parent_management.families.services import create_family, add_parent_to_family, \
    add_student_profile_to_family
from open_schools_platform.student_management.student.services import create_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_url = reverse("api:student-management:create-student-profile")
        self.student_join_circle_query_url = lambda pk: reverse("api:student-management:student-join-circle-query",
                                                                args=[pk])

    def test_family_does_not_exist(self):
        user = create_logged_in_user(instance=self)
        data_for_student_profile_create_request = {
            "age": 15,
            "name": "test_student_profile",
            "family": "99999999-9999-9999-9999-999999999999",
        }
        response_for_student_profile_create_request = self.client.post(self.student_profile_url,
                                                                       data_for_student_profile_create_request)
        self.assertEqual(404, response_for_student_profile_create_request.status_code)

        student_profile = create_student_profile(name="test_name", age=15)
        family = create_family("Simpsons")
        add_parent_to_family(family=family, parent=user.parent_profile)
        add_student_profile_to_family(family=family, student_profile=student_profile)

        data_for_student_profile_update_request = {
            "student_profile": student_profile.id,
            "family": "99999999-9999-9999-9999-999999999999",
            "age": 15,
            "name": "test_student_profile"
        }
        response_for_student_profile_update_request = self.client.put(self.student_profile_url,
                                                                      data_for_student_profile_update_request)
        self.assertEqual(404, response_for_student_profile_update_request.status_code)

    def test_current_user_cannot_interact_with_student_profile(self):
        create_logged_in_user(instance=self)
        family = create_family(name="test_family")
        data_for_student_profile_create_request = {
            "age": 15,
            "name": "test_student_profile",
            "family": family.id,
        }
        response_for_student_profile_create_request = self.client.post(self.student_profile_url,
                                                                       data_for_student_profile_create_request)
        self.assertEqual(403, response_for_student_profile_create_request.status_code)

        student_profile = create_student_profile(name="test_name", age=15)
        data_for_student_profile_update_request_with_family = {
            "student_profile": student_profile.id,
            "family": family.id,
            "age": 15,
            "name": "test_name"
        }
        response_for_student_profile_update_request_with_family = \
            self.client.put(self.student_profile_url, data_for_student_profile_update_request_with_family)
        self.assertEqual(403, response_for_student_profile_update_request_with_family.status_code)

        data_for_student_profile_update_request = {
            "student_profile": student_profile.id,
            "age": 15,
            "name": "test_name"
        }
        response_for_student_profile_update_request = self.client.put(self.student_profile_url,
                                                                      data_for_student_profile_update_request)
        self.assertEqual(403, response_for_student_profile_update_request.status_code)

    def test_student_profile_does_not_exist(self):
        create_logged_in_user(instance=self)
        data_for_student_profile_update_request = {
            "student_profile": "99999999-9999-9999-9999-999999999999",
            "age": 15,
            "name": "test_name"
        }
        response_for_student_profile_update_request = self.client.put(self.student_profile_url,
                                                                      data_for_student_profile_update_request)
        self.assertEqual(404, response_for_student_profile_update_request.status_code)

    def test_family_already_exists(self):
        user = create_logged_in_user(instance=self)
        family = create_family(name="test_family")
        family.parent_profiles.add(user.parent_profile)
        circle = create_test_circle()
        data_for_student_join_circle_request = {
            "name": 'test_name',
            "age": 15
        }
        response_for_student_join_circle_request = self.client.post(self.student_join_circle_query_url(circle.id),
                                                                    data_for_student_join_circle_request)
        self.assertEqual(406, response_for_student_join_circle_request.status_code)
