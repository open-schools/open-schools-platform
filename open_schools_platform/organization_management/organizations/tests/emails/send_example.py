from django.test import TestCase
from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.tasks.tasks import send_mail_to_new_user_with_celery


class TestSender(TestCase):

    def test_SDK_send_with_celery(self):
        send_mail_to_new_user_with_celery.delay("TEST",
                                                {'login': 'TEST_LOGIN', 'password': 'TEST_PASSWORD',
                                                 'organization': 'TEST_ORGANIZATION', 'name': 'TEST_NAME'},
                                                CommonConstants.DEFAULT_FROM_EMAIL,
                                                CommonConstants.TEST_EMAIL
                                                )
