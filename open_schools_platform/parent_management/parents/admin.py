from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.parent_management.parents.models import ParentProfile


@admin_wrapper(ParentProfile)
class ParentProfileAdmin(BaseAdmin):
    list_display = ('name', 'user', 'id')
    search_fields = ('name', 'user__phone')
