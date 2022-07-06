from django.test import TestCase
from django.core.exceptions import ValidationError

from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.user_management.users.services import create_user
from open_schools_platform.user_management.users.models import User


class UserCreateTests(TestCase):
    def test_user_with_not_valid_phone_cannot_be_created(self):
        create_user(
            phone="+79020000003",
            name="Alex Nevsky",
            password="qwerty123456",
        )

        with self.assertRaises(ValidationError):
            create_user(
                phone="+791121129",
                name="Alex Nevsky",
                password="qwerty123456",
            )

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmployeeProfile.objects.count())
        self.assertEqual(1, ParentProfile.objects.count())
        self.assertEqual(1, StudentProfile.objects.count())
