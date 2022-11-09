import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.student_management.students.tests.utils import create_test_student
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class StudentExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_logged_in_user(self)
        self.delete_student_url = lambda pk: reverse("api:students-management:students:delete-student", args=[pk])

    def test_delete_student_does_not_exist(self):
        response = self.client.delete(self.delete_student_url(uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_student_delete_wrong_access(self):
        student = create_test_student(create_test_circle(), create_test_user("+79997561212").student_profile)
        response = self.client.delete(self.delete_student_url(student.id))
        self.assertEqual(403, response.status_code)
