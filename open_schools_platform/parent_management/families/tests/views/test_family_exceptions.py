from django.test import TestCase
from django.urls import reverse

from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.user_management.users.services import create_user
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyExceptionsTests(TestCase):
    def setUp(self):
        self.user = create_logged_in_user(instance=self)
        self.studentprofiles_list_url = lambda pk: reverse("api:parent-management:families:student-profiles-list",
                                                           args=[pk])
        self.families_list_url = reverse("api:parent-management:families:family-api")

    def test_family_does_not_exists(self):
        not_logged_user = create_user(name="no_logged_user", password="azaza", phone="+79042282282")
        create_family(parent=not_logged_user.parent_profile)
        not_existing_pk = "99999999-9999-9999-9999-999999999999"
        studentprofiles_list_response = self.client.get(self.studentprofiles_list_url(not_existing_pk))
        self.assertEqual(404, studentprofiles_list_response.status_code)  # wrong family pk

        families_list_response = self.client.get(self.families_list_url)
        self.assertEqual(404, families_list_response.status_code)  # no families for logged user

    def test_permission(self):
        not_logged_user = create_user(name="Mashka", password="qwerty", phone="+79042282282")
        not_my_family = create_family(parent=not_logged_user.parent_profile)

        response = self.client.get(self.studentprofiles_list_url(not_my_family.id))
        self.assertEqual(403, response.status_code)
