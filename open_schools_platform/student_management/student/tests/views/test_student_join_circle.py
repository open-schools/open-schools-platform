from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.student.models import Student
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentJoinCirclesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_join_circle_query_url = lambda pk: reverse("api:student-management:student-join-circle-query",
                                                                args=[pk])

    def test_student_join_circle_query_successfully_formed(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle()
        data = {
            "name": "test_name",
            "age": 15
        }
        response = self.client.post(self.student_join_circle_query_url(circle.id), data)
        self.assertEqual(201, response.status_code)
        self.assertTrue(get_student_profile(filters={"name": data["name"]}))
        family = get_family(filters={"parent_profiles": str(user.parent_profile.id)})
        self.assertTrue(family)
        self.assertTrue(get_student_profile(filters={"name": data["name"]}) in family.student_profiles.all())
        self.assertTrue(user.parent_profile in family.parent_profiles.all())
        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Query.objects.count())
