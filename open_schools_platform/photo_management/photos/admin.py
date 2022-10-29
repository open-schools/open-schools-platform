from django.contrib import admin
from open_schools_platform.photo_management.photos.models import Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')


admin.site.register(Photo, PhotoAdmin)
