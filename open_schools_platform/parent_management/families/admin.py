from django.contrib import admin

from open_schools_platform.common.models import DeleteAdmin
from open_schools_platform.parent_management.families.models import Family


class FamilyAdmin(DeleteAdmin):
    list_display = DeleteAdmin.list_display + ('id',)
    search_fields = ("name",)
    list_filter = DeleteAdmin.list_filter


DeleteAdmin.init_model(FamilyAdmin)
admin.site.register(Family, FamilyAdmin)
