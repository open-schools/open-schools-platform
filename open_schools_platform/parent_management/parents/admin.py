from django.contrib import admin

from open_schools_platform.parent_management.parents.models import ParentProfile


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
