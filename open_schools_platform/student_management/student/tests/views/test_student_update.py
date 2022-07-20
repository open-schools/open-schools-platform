from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_update_url = reverse("api:student-management:create-student-profile")

    def test_successful_student_profile_update(self):
        user = create_logged_in_user(instance=self)
        student_profiles_name_update_request_data = {
            "student_profile": user.student.id,
            "name": "changed_name"
        }
        student_profiles_name_update_request_response =\
            self.client.put(self.student_profile_update_url, student_profiles_name_update_request_data)
        self.assertEqual(200, student_profiles_name_update_request_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student.id})
        self.assertEqual('changed_name', updated_student_profile.name)
        student_profiles_age_update_request_data = {
            "student_profile": user.student.id,
            "age": 16
        }
        student_profiles_age_update_request_response = self.client.put(self.student_profile_update_url,
                                                                       student_profiles_age_update_request_data)
        self.assertEqual(200, student_profiles_age_update_request_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student.id})
        self.assertEqual(16, updated_student_profile.age)
        student_profiles_age_and_name_update_request_data = {
            "student_profile": user.student.id,
            "age": 18,
            "name": "new_changed_name"
        }
        student_profiles_age_and_name_update_request_response = \
            self.client.put(self.student_profile_update_url, student_profiles_age_and_name_update_request_data)
        self.assertEqual(200, student_profiles_age_and_name_update_request_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student.id})
        self.assertEqual(18, updated_student_profile.age)
        self.assertEqual("new_changed_name", updated_student_profile.name)

    def test_successful_student_profile_in_family_update(self):
        user = create_logged_in_user(instance=self)
        family = create_family(name="test_family", parent=user.parent_profile)
        student_profile_in_family_update_request_data = {
            "student_profile": user.student.id,
            "family": family.id,
            "age": 16,
            "name": "changed_name"
        }
        student_profile_in_family_update_request_response = \
            self.client.put(self.student_profile_update_url, student_profile_in_family_update_request_data)
        self.assertEqual(200, student_profile_in_family_update_request_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student.id})
        self.assertEqual(16, updated_student_profile.age)
        self.assertEqual("changed_name", updated_student_profile.name)
