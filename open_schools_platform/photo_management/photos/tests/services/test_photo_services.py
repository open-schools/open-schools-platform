from django.test import TestCase

from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.photo_management.photos.services import update_photo
from open_schools_platform.photo_management.photos.tests.utils import create_test_photo


class CreatePhotoTests(TestCase):
    def test_successful_photo_creation(self):
        create_test_photo()
        self.assertEqual(1, Photo.objects.count())


class PhotoUpdateTests(TestCase):
    def test_photo_successfully_updated(self):
        photo = create_test_photo()
        update_photo(photo=photo, data={'image': None})
        self.assertEqual(photo.image, None)
