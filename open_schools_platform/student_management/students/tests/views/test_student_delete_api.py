from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.student_management.students.selectors import get_students
from open_schools_platform.student_management.students.tests.utils import get_deleted_students, \
    create_test_student_with_user_in_organization, create_test_student_with_user_in_parental_status
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(self)
        self.delete_student_url = lambda pk: reverse("api:students-management:students:delete-student", args=[pk])

    def test_successful_student_delete_by_employee(self):
        student = create_test_student_with_user_in_organization(self.user)
        response = self.client.delete(self.delete_student_url(student.id))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_students()))
        self.assertEqual(1, len(get_deleted_students()))

    def test_successful_student_delete_by_parent(self):
        student = create_test_student_with_user_in_parental_status(self.user)
        response = self.client.delete(self.delete_student_url(student.id))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_students()))
        self.assertEqual(1, len(get_deleted_students()))
