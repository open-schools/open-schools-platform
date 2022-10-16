from open_schools_platform.photo_management.photos.models import Photo


def create_test_photo() -> Photo:
    return Photo.objects.create_photo()
