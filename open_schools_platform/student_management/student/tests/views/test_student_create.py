from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.services import create_family, add_parent_to_family
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_create_url = reverse("api:student-management:create-student-profile")

    def test_successful_student_profile_creation(self):
        user = create_logged_in_user(instance=self)

        parent = get_parent_profile(filters={"user": user})
        family = create_family(name="Test_name")
        add_parent_to_family(family=family, parent=parent)

        data_for_student_profile_creation = {
            "name": "test_student_profile",
            "age": 15,
            "family": family.id
        }
        response_for_student_profile_creation = self.client.post(self.student_profile_create_url,
                                                                 data_for_student_profile_creation)
        self.assertEqual(201, response_for_student_profile_creation.status_code)
