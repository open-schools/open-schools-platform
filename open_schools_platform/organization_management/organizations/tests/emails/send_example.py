from django.test import TestCase
from open_schools_platform.common.constants import EmailConstants
from open_schools_platform.tasks.tasks import send_message_to_new_user_with_celery


class TestSender(TestCase):
    """run for debug sending mail"""
    def test_SDK_send_with_celery(self):
        send_message_to_new_user_with_celery.delay("TEST",
                                                   {'login': 'TEST_LOGIN', 'password': 'TEST_PASSWORD',
                                                 'organization': 'TEST_ORGANIZATION', 'name': 'TEST_NAME'},
                                                   EmailConstants.DEFAULT_FROM_EMAIL,
                                                   EmailConstants.TEST_EMAIL
                                                   )
