from django.test import TestCase

from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.services import create_family, add_parent_profile_to_family, \
    add_student_profile_to_family
from open_schools_platform.student_management.student.services import create_student_profile
from open_schools_platform.user_management.users.tests.utils import create_test_user


class CreateFamilyTests(TestCase):
    def test_successful_family_creation(self):
        user = create_test_user()
        create_family(name="test_family", parent=user.parent_profile)
        self.assertEqual(1, Family.objects.count())

    def test_successfully_generate_name_for_family(self):
        user = create_test_user()
        family = create_family(parent=user.parent_profile)
        self.assertTrue(family.name)


class AddParentToFamilyTests(TestCase):
    def test_successfully_add_parent_to_family(self):
        user1 = create_test_user()
        user2 = create_test_user(phone="+79020000000")
        family = create_family(name="test_family", parent=user1.parent_profile)
        add_parent_profile_to_family(family=family, parent=user2.parent_profile)
        self.assertTrue(user2.parent_profile in family.parent_profiles.all())


class AddStudentProfileToFamilyTests(TestCase):
    def test_successfully_add_student_profile_in_family(self):
        user = create_test_user()
        student_profile = create_student_profile(name="test_student_profile", age=15)
        family = create_family(name="test_family", parent=user.parent_profile)
        add_student_profile_to_family(family=family, student_profile=student_profile)
        self.assertTrue(student_profile in family.student_profiles.all())
