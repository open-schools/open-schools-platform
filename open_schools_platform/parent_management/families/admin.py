from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.parent_management.families.models import Family


@admin_wrapper(Family)
class FamilyAdmin(BaseAdmin):
    list_display = ('id',)
    search_fields = ("name",)
