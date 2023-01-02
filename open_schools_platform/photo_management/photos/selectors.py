from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.photo_management.photos.filters import PhotoFilter
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.user_management.users.models import User


@selector_factory(Photo)
def get_photo(*, filters=None, user: User = None) -> Photo:
    filters = filters or {}

    qs = Photo.objects.all()
    photo = PhotoFilter(filters, qs).qs.first()

    if user and photo and not user.has_perm('photos.photo_access', photo):
        raise PermissionDenied

    return photo
