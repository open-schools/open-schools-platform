from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.tests.utils import create_test_student_join_circle_query
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.student_management.students.selectors import get_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class StudentJoinCirclesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_join_circle_query_url = reverse("api:students-management:students:auto-student-join-circle-query")
        self.student_join_circle_query_update_url = \
            reverse("api:students-management:students:student-join-circle-update-query")

    def test_student_join_circle_query_successfully_formed(self):
        user = create_logged_in_user(instance=self)
        circle = create_test_circle()
        data = {
            "student_profile": {
                "name": "test_name",
                "age": 15,
            },
            "additional": {
                "text": "Please, let me in!",
            },
            "circle": circle.id,
        }
        response = self.client.post(self.student_join_circle_query_url, data, format="json")
        self.assertEqual(201, response.status_code)
        self.assertTrue(get_student_profile(filters={"name": data["student_profile"]["name"]}))
        family = get_family(filters={"parent_profiles": str(user.parent_profile.id)})
        self.assertTrue(family)
        self.assertTrue(get_student_profile(
            filters={"name": data["student_profile"]["name"]}) in family.student_profiles.all())
        self.assertTrue(user.parent_profile in family.parent_profiles.all())
        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Query.objects.count())

    def test_student_join_circle_query_successfully_updated(self):
        user = create_logged_in_user(instance=self)
        query = create_test_student_join_circle_query(user)
        data = {
              "query": str(query.id),
              "body": {
                "name": "new-test-name"
              }
        }
        response = self.client.put(self.student_join_circle_query_update_url, data, format="json")
        print(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue(query.body.name == "new-test-name")
