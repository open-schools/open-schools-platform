from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.organization_management.circles.tests.utils import \
    create_test_circle_with_user_in_org, create_data_circle_invite_student
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import create_family, add_student_profile_to_family
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.student_management.students.selectors import get_student_profile
from open_schools_platform.student_management.students.services import create_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user
from phonenumber_field.phonenumber import PhoneNumber


class InviteStudentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invite_student_url = \
            lambda pk: reverse("api:organization-management:circles:invite-student", args=[pk])

    def test_invite_student_query_successfully_formed_1(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=user)

        data = create_data_circle_invite_student("TestStudent", "+79961700000", "+79961700001")

        response = self.client.post(self.invite_student_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)
        parent_profile = get_parent_profile(filters={"phone": data["parent_phone"]})
        self.assertTrue(parent_profile)
        family = get_family(filters={"parent_profiles": str(parent_profile.id)})
        self.assertTrue(family)
        families = parent_profile.families.all()
        student_profile = get_student_profile(filters={"families": form_ids_string_from_queryset(families)})
        self.assertTrue(student_profile)

    def test_invite_student_query_successfully_formed_2(self):
        circle_owner = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=circle_owner)
        parent1 = create_test_user(phone="+79961700002")

        data = create_data_circle_invite_student("TestStudent", "+79961700003", str(parent1.phone))

        response = self.client.post(self.invite_student_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)
        family = get_family(filters={"parent_profiles": str(parent1.parent_profile.id)})
        self.assertTrue(family)
        families = parent1.parent_profile.families.all()
        student_profile = get_student_profile(filters={"families": form_ids_string_from_queryset(families)})
        self.assertTrue(student_profile)

    def test_invite_student_query_successfully_formed_3(self):
        circle_owner = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=circle_owner)
        parent1 = create_test_user(phone="+79961700004")
        parent2 = create_test_user(phone="+79961700013")
        create_family(parent=parent1.parent_profile)
        create_family(parent=parent1.parent_profile)
        create_family(parent=parent2.parent_profile)

        data = create_data_circle_invite_student("TestStudent", "+79961700005", str(parent1.phone))

        response = self.client.post(self.invite_student_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)
        families = parent1.parent_profile.families.all()
        student_profile = get_student_profile(filters={"families": form_ids_string_from_queryset(families)})
        self.assertTrue(student_profile)

    def test_invite_student_query_successfully_formed_4(self):
        circle_owner = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=circle_owner)
        parent1 = create_test_user(phone="+79961700006")
        student_profile = create_student_profile(phone=PhoneNumber.from_string("+79961700007"),
                                                 name="TestStudent")
        parent_family = create_family(parent=parent1.parent_profile)
        add_student_profile_to_family(family=parent_family, student_profile=student_profile)

        data = create_data_circle_invite_student(str(student_profile.name), str(student_profile.phone),
                                                 str(parent1.phone))

        response = self.client.post(self.invite_student_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)

    def test_invite_student_query_successfully_formed_5(self):
        circle_owner = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=circle_owner)
        parent1 = create_test_user(phone="+79961700008")
        parent2 = create_test_user(phone="+79961700009")
        family1 = create_family(parent=parent1.parent_profile)
        family2 = create_family(parent=parent2.parent_profile)
        family3 = create_family(parent=parent1.parent_profile)
        student_profile = create_student_profile(phone=PhoneNumber.from_string("+79961700010"), name="TestStudent")
        student_profile2 = create_student_profile(phone=PhoneNumber.from_string("+79961700014"), name="AnotherStudent1")
        student_profile3 = create_student_profile(phone=PhoneNumber.from_string("+79961700015"), name="AnotherStudent2")
        add_student_profile_to_family(family=family2, student_profile=student_profile)
        add_student_profile_to_family(family=family1, student_profile=student_profile2)
        add_student_profile_to_family(family=family1, student_profile=student_profile3)
        add_student_profile_to_family(family=family3, student_profile=student_profile3)

        data = create_data_circle_invite_student(str(student_profile.name), str(student_profile.phone),
                                                 str(parent1.phone))

        response = self.client.post(self.invite_student_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)
        families = parent1.parent_profile.families.all()
        new_student_profile = get_student_profile(filters={"families": form_ids_string_from_queryset(families)})
        self.assertTrue(new_student_profile)
        self.assertEqual(student_profile.phone, new_student_profile.phone)
        self.assertNotEqual(student_profile2.phone, new_student_profile.phone)
        self.assertNotEqual(student_profile3.phone, new_student_profile.phone)
