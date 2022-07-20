from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.services import create_family, add_parent_to_family
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_update_url = reverse("api:student-management:create-student-profile")

    def test_successful_student_profile_update(self):
        user = create_logged_in_user(instance=self)
        data_for_student_profiles_name_update_request = {
            "student_profile": user.student_profile.id,
            "name": "changed_name"
        }
        response_for_student_profiles_name_update_request =\
            self.client.put(self.student_profile_update_url, data_for_student_profiles_name_update_request)
        self.assertEqual(200, response_for_student_profiles_name_update_request.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual('changed_name', updated_student_profile.name)
        data_for_student_profiles_age_update_request = {
            "student_profile": user.student_profile.id,
            "age": 16
        }
        response_for_student_profiles_age_update_request = self.client.put(self.student_profile_update_url,
                                                                           data_for_student_profiles_age_update_request)
        self.assertEqual(200, response_for_student_profiles_age_update_request.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(16, updated_student_profile.age)
        data_for_student_profiles_age_and_name_update_request = {
            "student_profile": user.student_profile.id,
            "age": 18,
            "name": "new_changed_name"
        }
        response_for_student_profiles_age_and_name_update_request = \
            self.client.put(self.student_profile_update_url, data_for_student_profiles_age_and_name_update_request)
        self.assertEqual(200, response_for_student_profiles_age_and_name_update_request.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(18, updated_student_profile.age)
        self.assertEqual("new_changed_name", updated_student_profile.name)

    def test_successful_student_profile_in_family_update(self):
        user = create_logged_in_user(instance=self)
        family = create_family(name="test_family")
        add_parent_to_family(family=family, parent=user.parent_profile)
        data = {
            "student_profile": user.student_profile.id,
            "family": family.id,
            "age": 16,
            "name": "changed_name"
        }
        response_for_student_profile_in_family_update_request = self.client.put(self.student_profile_update_url, data)
        self.assertEqual(200, response_for_student_profile_in_family_update_request.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(16, updated_student_profile.age)
        self.assertEqual("changed_name", updated_student_profile.name)
