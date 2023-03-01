from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.photo_management.photos.models import Photo


@admin_wrapper(Photo)
class PhotoAdmin(BaseAdmin):
    list_display = ('id', 'image')
    field_to_highlight = 'id'
