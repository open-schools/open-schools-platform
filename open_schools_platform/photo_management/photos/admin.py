from django.contrib import admin

from open_schools_platform.common.admin import admin_wrapper
from open_schools_platform.photo_management.photos.models import Photo


@admin_wrapper(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')
