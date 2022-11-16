import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.photo_management.photos.tests.utils import create_test_photo
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class PhotoExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.query_photo_update_url = lambda pk: reverse("api:photo-management:photos:create-photo", args=[pk])

    def test_update_photo_with_wrong_permissions(self):
        create_logged_in_user(self)
        photo = create_test_photo()
        response_for_unattached_photo = self.client.patch(self.query_photo_update_url(photo.id))
        self.assertEqual(403, response_for_unattached_photo.status_code)
        user = create_test_user('+78085456422')
        response_for_wrong_user = self.client.patch(self.query_photo_update_url(user.student_profile.photo.id))
        self.assertEqual(403, response_for_wrong_user.status_code)

    def test_photo_does_not_exist(self):
        create_logged_in_user(self)
        non_existed_id = uuid.uuid4()
        response = self.client.patch(self.query_photo_update_url(non_existed_id))
        self.assertEqual(404, response.status_code)
