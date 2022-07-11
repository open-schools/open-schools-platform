from django.test import TestCase

from open_schools_platform.parent_management.families.services import create_family, add_parent_to_family
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.student_management.student.services import create_student_profile, \
    can_user_interact_with_student_profile_check, update_student_profile
from open_schools_platform.user_management.users.services import create_user


class CreateStudentProfileTests(TestCase):
    def test_successful_student_profile_creation(self):
        create_student_profile(name="test_student_profile", age=15)
        self.assertEqual(1, StudentProfile.objects.count())


class CanUserInteractWithStudentProfileCheckTests(TestCase):
    def test_user_can_interact_with_student_profile(self):
        user = create_user(
            phone="+79020000000",
            password="123456",
            name="test_user"
        )
        family = create_family(name="test_family")
        add_parent_to_family(family=family, parent=user.parent_profile)
        result = can_user_interact_with_student_profile_check(family=family, user=user)
        self.assertTrue(result)

    def test_user_cannot_interact_with_student_profile(self):
        user = create_user(
            phone="+79020000000",
            password="123456",
            name="test_user"
        )
        family = create_family(name="test_family")
        result = can_user_interact_with_student_profile_check(family=family, user=user)
        self.assertFalse(result)


class UpdateStudentProfileTests(TestCase):
    def test_successful_student_profile_update(self):
        student_profile = create_student_profile(name="test_student_profile", age=15)
        data_for_student_profile_update = {
            "name": "new_name",
            "age": 18
        }
        update_student_profile(student_profile=student_profile, data=data_for_student_profile_update)
        self.assertEqual("new_name", student_profile.name)
        self.assertEqual(18, student_profile.age)
