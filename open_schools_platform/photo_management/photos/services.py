from datetime import datetime

from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.utils.hashes import hash_file


def create_photo(image: bytes = None) -> Photo:
    photo = Photo.objects.create_photo(
        image=image
    )
    return photo


def update_photo(*, photo: Photo, data) -> Photo:
    non_side_effect_fields = ['image']
    filtered_data = filter_dict_from_none_values(data)

    if 'image' in filtered_data:
        image = filtered_data["image"]
        image_hash = hash_file(image)
        cur_name = image.name

        filtered_data["image"].name = f"{image_hash}_{datetime.now()}.{cur_name.split('.')[-1]}"

    photo, has_updated = model_update(
        instance=photo,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return photo
