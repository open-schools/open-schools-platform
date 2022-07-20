from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentProfileCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_create_url = reverse("api:student-management:create-student-profile")

    def test_successful_student_profile_creation(self):
        user = create_logged_in_user(instance=self)
        family = create_family(name="Test_name", parent=user.parent_profile)

        student_profile_creation_data = {
            "name": "test_student_profile",
            "age": 15,
            "family": family.id
        }
        student_profile_creation_response = self.client.post(self.student_profile_create_url,
                                                             student_profile_creation_data)
        self.assertEqual(201, student_profile_creation_response.status_code)
        self.assertEqual(2, StudentProfile.objects.count())
        self.assertTrue(get_student_profile(filters={"age": 15}) in family.student_profiles.all())
