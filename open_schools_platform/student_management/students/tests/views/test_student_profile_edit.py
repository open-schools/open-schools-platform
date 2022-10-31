from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.student_management.students.selectors import get_student_profile, \
    get_student_profiles
from open_schools_platform.student_management.students.tests.utils import get_deleted_student_profiles
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_edit_url = lambda pk: \
            reverse("api:students-management:students:edit-student-profile", args=[pk])

    def test_successful_student_profile_update(self):
        user = create_logged_in_user(instance=self)
        student_profiles_name_update_data = {
            "name": "changed_name"
        }
        student_profiles_name_update_response = \
            self.client.put(self.student_profile_edit_url(str(user.student_profile.id)),
                            student_profiles_name_update_data)
        self.assertEqual(200, student_profiles_name_update_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual('changed_name', updated_student_profile.name)
        student_profiles_age_update_data = {
            "age": 16
        }
        student_profiles_age_update_response = self.client.put(self.student_profile_edit_url
                                                               (str(user.student_profile.id)),
                                                               student_profiles_age_update_data)
        self.assertEqual(200, student_profiles_age_update_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(16, updated_student_profile.age)
        student_profiles_age_and_name_update_data = {
            "age": 18,
            "name": "new_changed_name"
        }
        student_profiles_age_and_name_update_response = \
            self.client.put(self.student_profile_edit_url(str(user.student_profile.id)),
                            student_profiles_age_and_name_update_data)
        self.assertEqual(200, student_profiles_age_and_name_update_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(18, updated_student_profile.age)
        self.assertEqual("new_changed_name", updated_student_profile.name)

    def test_successful_student_profile_in_family_update(self):
        user = create_logged_in_user(instance=self)
        family = create_family(name="test_family", parent=user.parent_profile)
        student_profile_in_family_update_data = {
            "family": family.id,
            "age": 16,
            "name": "changed_name"
        }
        student_profile_in_family_update_response = \
            self.client.put(self.student_profile_edit_url(str(user.student_profile.id)),
                            student_profile_in_family_update_data)
        self.assertEqual(200, student_profile_in_family_update_response.status_code)
        updated_student_profile = get_student_profile(filters={"id": user.student_profile.id})
        self.assertEqual(16, updated_student_profile.age)
        self.assertEqual("changed_name", updated_student_profile.name)

    def test_successful_student_profile_delete(self):
        user = create_logged_in_user(self)
        response = self.client.delete(self.student_profile_edit_url(user.student_profile.id))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(get_student_profiles()))
        self.assertEqual(1, len(get_deleted_student_profiles()))
