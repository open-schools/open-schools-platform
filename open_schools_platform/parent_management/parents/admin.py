from django.contrib import admin

from open_schools_platform.common.admin import admin_wrapper
from open_schools_platform.parent_management.parents.models import ParentProfile


@admin_wrapper(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'id')
    search_fields = ('name', 'user__phone')
