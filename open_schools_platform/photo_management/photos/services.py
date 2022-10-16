from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.user_management.users.models import User


def create_photo(image: bytes = None) -> Photo:
    photo = Photo.objects.create_photo(
        image=image
    )
    return photo


def update_photo(*, photo: Photo, data, user: User = None) -> Photo:
    non_side_effect_fields = ['image']
    filtered_data = filter_dict_from_none_values(data)

    if user and photo and not user.has_perm('photos.photo_access', photo):
        raise PermissionDenied

    photo, has_updated = model_update(
        instance=photo,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return photo
