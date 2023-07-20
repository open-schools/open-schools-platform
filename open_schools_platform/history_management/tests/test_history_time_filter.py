import json

from django.test import TestCase
from rest_framework.test import APIClient
from freezegun import freeze_time

from open_schools_platform.common.utils import reverse_querystring
from open_schools_platform.student_management.students.services import update_student_profile
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class HistoryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_profile_history_url = lambda pk, kwargs=None: reverse_querystring(
            'api:history-management:history:student-profile-history',
            kwargs={'student_profile_id': pk}, query_kwargs=kwargs)

        self.user = create_logged_in_user(instance=self)

        with freeze_time('2200-01-01'):
            student_profiles_name_update_data = {
                "name": "changed_name1"
            }
            update_student_profile(student_profile=self.user.student_profile, data=student_profiles_name_update_data)

        with freeze_time('2200-01-02'):
            student_profiles_name_update_data = {
                "name": "changed_name2"
            }
            update_student_profile(student_profile=self.user.student_profile, data=student_profiles_name_update_data)

        with freeze_time('2200-01-03'):
            student_profiles_name_update_data = {
                "name": "changed_name3"
            }
            update_student_profile(student_profile=self.user.student_profile, data=student_profiles_name_update_data)

        with freeze_time('2200-01-04'):
            student_profiles_name_update_data = {
                "name": "changed_name4"
            }
            update_student_profile(student_profile=self.user.student_profile, data=student_profiles_name_update_data)

        with freeze_time('2200-01-05'):
            student_profiles_name_update_data = {
                "name": "changed_name5"
            }
            update_student_profile(student_profile=self.user.student_profile, data=student_profiles_name_update_data)

    def test_successfully_return_history_without_filter(self):
        full_response = self.client.get(self.student_profile_history_url(self.user.student_profile.id))
        self.assertEqual(200, full_response.status_code)
        result = json.loads(full_response.content)
        self.assertEqual(6, result['count'])

    def test_successfully_filter_history_by_begin_date(self):
        only_begin_response = self.client.get(
            self.student_profile_history_url(self.user.student_profile.id, {'begin_date': '2200-01-04'}))
        self.assertEqual(200, only_begin_response.status_code)
        result = json.loads(only_begin_response.content)
        self.assertEqual(2, result['count'])

    def test_successfully_filter_history_by_end_date(self):
        only_end_response = self.client.get(
            self.student_profile_history_url(self.user.student_profile.id, {'end_date': '2200-01-02'}))
        self.assertEqual(200, only_end_response.status_code)
        result = json.loads(only_end_response.content)
        self.assertEqual(3, result['count'])

    def test_successfully_filter_history_by_date_range(self):
        time_range_response = self.client.get(
            self.student_profile_history_url(self.user.student_profile.id,
                                             {'begin_date': '2200-01-03', 'end_date': '2200-01-04'}))
        self.assertEqual(200, time_range_response.status_code)
        result = json.loads(time_range_response.content)
        self.assertEqual(2, result['count'])

    def test_bad_request_on_wrong_date_range(self):
        wrong_range_response = self.client.get(
            self.student_profile_history_url(self.user.student_profile.id,
                                             {'begin_date': '2300-01-01', 'end_date': '2100-01-01'}))
        self.assertEqual(400, wrong_range_response.status_code)
