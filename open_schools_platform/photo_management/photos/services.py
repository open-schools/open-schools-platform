from open_schools_platform.photo_management.photos.models import Photo


def create_photo(image: bytes = None) -> Photo:
    photo = Photo.objects.create_photo(
        image=image
    )
    return photo
