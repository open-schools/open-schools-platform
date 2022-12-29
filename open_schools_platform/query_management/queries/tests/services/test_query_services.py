from django.test import TestCase

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update, run_sender_handler
from open_schools_platform.query_management.queries.tests.utils import create_test_student_join_circle_query
from open_schools_platform.student_management.students.models import Student, StudentProfileCircleAdditional
from open_schools_platform.user_management.users.tests.utils import create_test_user


class CreateQueryTests(TestCase):
    def test_successful_query_creation(self):
        create_test_student_join_circle_query()
        self.assertEqual(1, Student.objects.count())
        self.assertEqual(1, Query.objects.count())
        self.assertEqual(1, StudentProfileCircleAdditional.objects.count())


class QueryUpdateTests(TestCase):
    def test_query_successfully_updated(self):
        query = create_test_student_join_circle_query()
        query_update(query=query, data={'status': Query.Status.IN_PROGRESS})
        self.assertTrue(query.status == Query.Status.IN_PROGRESS)


class RunSenderHandlerTests(TestCase):
    def test_successfully_ran_sender_handler(self):
        user = create_test_user()
        circle = create_test_circle_with_user_in_org(user=user)
        query = create_test_student_join_circle_query(circle=circle)
        run_sender_handler(query=query, new_status=Query.Status.ACCEPTED, user=user)
        self.assertTrue(query.status == Query.Status.ACCEPTED)
        self.assertTrue(query.body.student_profile == query.sender)
        self.assertTrue(query.body.circle == query.recipient)
