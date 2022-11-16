from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.parent_management.families.tests.utils import create_test_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_query
from open_schools_platform.query_management.queries.tests.utils import create_test_student_join_circle_query, \
    create_test_family_invite_parent_query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentJoinCircleQueryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_status_change_url = reverse("api:query-management:queries:change-query-status")

    def test_user_changes_status_on_canceled(self):
        user = create_logged_in_user(instance=self)
        query = create_test_student_join_circle_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.CANCELED)

    def test_circle_changes_status_not_on_canceled(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=user)
        query = create_test_student_join_circle_query(circle=circle)
        data = {
            "id": query.id,
            "status": Query.Status.IN_PROGRESS
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.IN_PROGRESS)

    def test_circle_changes_status_on_accepted(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle_with_user_in_org(user=user)
        query = create_test_student_join_circle_query(circle=circle)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.ACCEPTED)
        self.assertTrue(query.body.student_profile == query.sender)
        self.assertTrue(query.body.circle == query.recipient)


class FamilyInviteParentQueryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_status_change_url = reverse("api:query-management:queries:change-query-status")

    def test_family_changes_status_on_canceled(self):
        user = create_logged_in_user(instance=self)
        family = create_test_family(i=1, parent=user.parent_profile)
        query = create_test_family_invite_parent_query(family=family)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.CANCELED)

    def test_parent_changes_status_not_on_accepted(self):
        user = create_logged_in_user(instance=self)
        query = create_test_family_invite_parent_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.DECLINED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.DECLINED)

    def test_parent_changes_status_on_accepted(self):
        user = create_logged_in_user(instance=self)
        query = create_test_family_invite_parent_query(user=user)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(get_query(filters={"id": str(query.id)}).status == Query.Status.ACCEPTED)
        self.assertTrue(query.recipient in query.sender.parent_profiles.all())
