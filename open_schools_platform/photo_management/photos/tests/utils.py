from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.photo_management.photos.services import create_photo


def create_test_photo(image: bytes = None) -> Photo:
    return create_photo(image)
