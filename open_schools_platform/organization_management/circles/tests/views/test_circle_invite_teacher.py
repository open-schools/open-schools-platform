from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org, \
    create_data_circle_invite_teacher, create_test_circle, create_test_query_circle_invite_teacher, \
    create_test_teacher_profile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class InviteTeacherTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invite_teacher_url = \
            lambda pk: reverse("api:organization-management:circles:invite-teacher", args=[pk])

    def test_invite_teacher_query_successfully_formed(self):
        user = create_logged_in_user(self)
        circle = create_test_circle_with_user_in_org(user)

        teacher_profile = create_test_teacher_profile("+79998786644")

        data = create_data_circle_invite_teacher("TestTeacher", str(teacher_profile.user.phone))

        response = self.client.post(self.invite_teacher_url(str(circle.id)), data, format="json")
        self.assertEqual(201, response.status_code)


class CircleInviteTeacherQueryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_status_change_url = reverse("api:query-management:queries:change-query-status")

    def test_teacher_can_change_status_on_accepted(self):
        circle = create_test_circle()
        user = create_logged_in_user(self)
        teacher_profile = user.teacher_profile
        query = create_test_query_circle_invite_teacher(circle, teacher_profile)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(Query.Status.ACCEPTED, get_query(filters={"id": str(query.id)}).status)

    def test_teacher_can_change_status_on_declined(self):
        circle = create_test_circle()
        user = create_logged_in_user(self)
        teacher_profile = user.teacher_profile
        query = create_test_query_circle_invite_teacher(circle, teacher_profile)
        data = {
            "id": query.id,
            "status": Query.Status.DECLINED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(Query.Status.DECLINED, get_query(filters={"id": str(query.id)}).status)

    def test_circle_can_change_status_on_canceled(self):
        circle_owner = create_logged_in_user(self)
        circle = create_test_circle_with_user_in_org(user=circle_owner)
        user = create_test_user(phone="+79998880008")
        teacher_profile = user.teacher_profile
        query = create_test_query_circle_invite_teacher(circle, teacher_profile)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(Query.Status.CANCELED, get_query(filters={"id": str(query.id)}).status)

    def test_circle_cannot_change_status_not_on_canceled(self):
        circle_owner = create_logged_in_user(self)
        circle = create_test_circle_with_user_in_org(circle_owner)
        user = create_test_user(phone="+79998880008")
        teacher_profile = user.teacher_profile
        query = create_test_query_circle_invite_teacher(circle, teacher_profile)
        data = {
            "id": query.id,
            "status": Query.Status.ACCEPTED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)
        self.assertEqual(Query.Status.SENT, get_query(filters={"id": str(query.id)}).status)

    def test_teacher_cannot_change_status_to_canceled(self):
        user = create_logged_in_user(self)
        circle = create_test_circle()
        teacher_profile = user.teacher_profile
        query = create_test_query_circle_invite_teacher(circle, teacher_profile)
        data = {
            "id": query.id,
            "status": Query.Status.CANCELED
        }
        response = self.client.patch(self.query_status_change_url, data)
        self.assertEqual(406, response.status_code)
        self.assertEqual(Query.Status.SENT, get_query(filters={"id": str(query.id)}).status)
