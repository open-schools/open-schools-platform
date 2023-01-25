import uuid

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.circles.tests.utils import get_deleted_circles, \
    create_test_circle_with_user_in_org, create_test_circle, create_data_circle_invite_teacher
from open_schools_platform.student_management.students.tests.utils import create_test_student
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CircleDeleteApiExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.circle_url = lambda pk: reverse("api:organization-management:circles:circle", args=[pk])
        self.export_students_url = lambda pk: reverse("api:organization-management:circles:students-export", args=[pk])
        self.invite_teacher_url = \
            lambda pk: reverse("api:organization-management:circles:invite-teacher", args=[pk])

    def test_delete_circle_does_not_exist(self):
        user = create_logged_in_user(self)
        create_test_circle_with_user_in_org(user)
        response = self.client.delete(self.circle_url(pk=str(uuid.uuid4())))
        self.assertEqual(404, response.status_code)
        self.assertEqual(1, len(get_circles()))
        self.assertEqual(0, len(get_deleted_circles()))

    def test_delete_circle_wrong_access(self):
        create_logged_in_user(self)
        circle = create_test_circle()
        response = self.client.delete(self.circle_url(pk=circle.id))
        self.assertEqual(403, response.status_code)
        self.assertEqual(1, len(get_circles()))
        self.assertEqual(0, len(get_deleted_circles()))

    def test_export_students_wrong_access(self):
        create_logged_in_user(self)
        circle = create_test_circle()
        create_test_student(circle=circle)
        response = self.client.get(self.export_students_url(circle.pk))
        self.assertEqual(403, response.status_code)

    def test_invite_teacher_does_not_exist(self):
        create_logged_in_user(self)
        data = create_data_circle_invite_teacher("TestTeacher", "+79998881177")
        response = self.client.post(self.invite_teacher_url(str(uuid.uuid4())), data, format="json")
        self.assertEqual(404, response.status_code)
