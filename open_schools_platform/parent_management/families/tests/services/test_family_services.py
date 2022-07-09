from django.test import TestCase

from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.services import create_family, add_parent_to_family, \
    add_student_profile_to_family, generate_name_for_family
from open_schools_platform.student_management.student.services import create_student_profile
from open_schools_platform.user_management.users.services import create_user


class CreateFamilyTests(TestCase):
    def test_successful_family_creation(self):
        create_family(name="test_family")
        self.assertEqual(1, Family.objects.count())


class AddParentToFamilyTests(TestCase):
    def test_successfully_add_parent_to_family(self):
        user = create_user(
            phone="+79020000000",
            password="123456",
            name="test_user"
        )
        family = create_family(name="test_family")
        add_parent_to_family(family=family, parent=user.parent_profile)
        self.assertTrue(user.parent_profile in family.parent_profiles.all())


class AddStudentProfileToFamilyTests(TestCase):
    def test_successfully_add_student_profile_in_family(self):
        student_profile = create_student_profile(name="test_student_profile", age=15)
        family = create_family(name="test_family")
        add_student_profile_to_family(family=family, student_profile=student_profile)
        self.assertTrue(student_profile in family.student_profiles.all())


class GenerateNameForFamilyTests(TestCase):
    def test_successfully_generate_name_for_family(self):
        user = create_user(
            phone="+79020000000",
            password="123456",
            name="test_user"
        )
        family = create_family(name=generate_name_for_family(parent=user.parent_profile))
        self.assertTrue(family.name)
