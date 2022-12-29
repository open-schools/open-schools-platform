from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.photo_management.photos.models import Photo


class PhotoFilter(BaseFilterSet):
    class Meta:
        model = Photo
        fields = ('id',)
