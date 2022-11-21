from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.parent_management.families.tests.utils import create_test_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.tests.utils import create_test_student_join_circle_query, \
    change_test_query_status, create_test_employee_invite_organization_query, create_test_family_invite_parent_query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentJoinCircleQueryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_status_change_url = reverse("api:query-management:queries:change-query-status")

    def test_user_set_status_not_from_allowed_statuses(self):
        user = create_logged_in_user(instance=self)

        query = create_test_employee_invite_organization_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.IN_PROGRESS
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_set_invalid_status(self):
        user = create_logged_in_user(instance=self)
        query = create_test_student_join_circle_query(user=user)
        data = {
            "id": query.id,
            "status": "invalid_status"
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(400, response.status_code)

    def test_user_set_not_canceled_status(self):
        user = create_logged_in_user(instance=self)
        query = create_test_student_join_circle_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_user_can_no_longer_change_query(self):
        user = create_logged_in_user(instance=self)
        query = create_test_student_join_circle_query(user=user)
        change_test_query_status(query=query, new_status=Query.Status.IN_PROGRESS)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_circle_set_canceled_status(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=user)
        query = create_test_student_join_circle_query(circle=circle)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_circle_can_no_longer_change_query(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=user)
        query = create_test_student_join_circle_query(circle=circle)
        change_test_query_status(query=query, new_status=Query.Status.CANCELED)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)


class FamilyInviteParentQueryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_status_change_url = reverse("api:query-management:queries:change-query-status")

    def test_set_invalid_status(self):
        user = create_logged_in_user(instance=self)
        query = create_test_family_invite_parent_query(user=user)
        data = {
            "id": query.id,
            "status": "invalid_status"
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(400, response.status_code)

    def test_family_set_not_canceled_status(self):
        user = create_logged_in_user(instance=self)
        family = create_test_family(i=1, parent=user.parent_profile)
        query = create_test_family_invite_parent_query(family=family)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_parent_can_no_longer_change_query(self):
        user = create_logged_in_user(instance=self)
        query = create_test_family_invite_parent_query(user=user)
        change_test_query_status(query=query, new_status=Query.Status.CANCELED)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_parent_set_canceled_status(self):
        user = create_logged_in_user(instance=self)
        query = create_test_family_invite_parent_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)

    def test_family_can_no_longer_change_query(self):
        user = create_logged_in_user(instance=self)
        family = create_test_family(i=1, parent=user.parent_profile)
        query = create_test_family_invite_parent_query(family=family)
        change_test_query_status(query=query, new_status=Query.Status.ACCEPTED)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)
