from django.test import TestCase
from django.urls import reverse

from open_schools_platform.parent_management.families.services import create_family, add_parent_profile_to_family
from open_schools_platform.user_management.users.services import create_user
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class FamilyExceptionsTests(TestCase):
    def setUp(self):
        self.user = create_logged_in_user(instance=self)
        self.studentprofiles_list_url = lambda pk: reverse("api:parent-management:families:student-profiles-list",
                                                           args=[pk])
        self.families_list_url = reverse("api:parent-management:families:family-api")
        self.invite_parent_url = reverse("api:parent-management:families:invite-parent")

    def test_family_does_not_exists(self):
        not_logged_user = create_user(name="no_logged_user", password="azaza", phone="+79042282282")
        create_family(parent=not_logged_user.parent_profile)
        not_existing_pk = "99999999-9999-9999-9999-999999999999"
        studentprofiles_list_response = self.client.get(self.studentprofiles_list_url(not_existing_pk))
        self.assertEqual(404, studentprofiles_list_response.status_code)  # wrong family pk

        families_list_response = self.client.get(self.families_list_url)
        self.assertEqual(404, families_list_response.status_code)  # no families for logged user

        invite_parent_data = {
            "family": not_existing_pk,
            "phone": "+79022222222"
        }
        invite_parent_response = self.client.post(self.invite_parent_url, invite_parent_data)
        self.assertEqual(404, invite_parent_response.status_code)

    def test_permission(self):
        not_logged_user = create_user(name="Mashka", password="qwerty", phone="+79042282282")
        not_my_family = create_family(parent=not_logged_user.parent_profile)

        studentprofiles_list_response = self.client.get(self.studentprofiles_list_url(not_my_family.id))
        self.assertEqual(403, studentprofiles_list_response.status_code)

        invite_parent_data_with_not_my_family = {
            "family": str(not_my_family.id),
            "phone": not_logged_user.phone,
        }
        invite_parent_with_not_my_family_response = self.client.post(self.invite_parent_url,
                                                                     invite_parent_data_with_not_my_family)
        self.assertEqual(403, invite_parent_with_not_my_family_response.status_code)

    def test_parent_profile_does_not_exist(self):
        family = create_family(parent=self.user.parent_profile)
        invite_parent_data = {
            "family": str(family.id),
            "phone": "+79022222222"
        }
        invite_parent_response = self.client.post(self.invite_parent_url, invite_parent_data)
        self.assertEqual(404, invite_parent_response.status_code)

    def test_parent_is_already_in_family(self):
        family = create_family(parent=self.user.parent_profile)
        parent = create_test_user(phone="+79022222222")
        add_parent_profile_to_family(family, parent.parent_profile)
        invite_parent_data = {
            "family": str(family.id),
            "phone": str(parent.phone)
        }
        invite_parent_response = self.client.post(self.invite_parent_url, invite_parent_data)
        self.assertEqual(406, invite_parent_response.status_code)
