from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.photo_management.photos.filters import PhotoFilter
from open_schools_platform.photo_management.photos.models import Photo


@selector_wrapper
def get_photo(*, filters=None) -> Photo:
    filters = filters or {}

    qs = Photo.objects.all()
    photo = PhotoFilter(filters, qs).qs.first()

    return photo
