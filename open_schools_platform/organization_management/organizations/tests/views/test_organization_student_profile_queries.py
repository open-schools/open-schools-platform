from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.query_management.queries.tests.utils import create_test_student_join_circle_query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class QueriesCirclesOrganizationStudentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.circle_organization_url = lambda organization_id, student_profile_id: reverse(
            "api:organization-management:organizations:queries-organization-student-profile",
            args=[organization_id, student_profile_id])

    def test_successfully_search_queries(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        circle = create_test_circle_with_user_in_org(user, organization)
        create_test_student_join_circle_query(user, circle)
        response = self.client.get(self.circle_organization_url(str(organization.id), str(user.student_profile.id)))
        self.assertEqual(200, response.status_code)
