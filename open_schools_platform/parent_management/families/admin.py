from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter

from open_schools_platform.parent_management.families.models import Family


class FamilyAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field", "id")
    search_fields = ("name",)
    list_filter = (SafeDeleteAdminFilter,) + SafeDeleteAdmin.list_filter

    field_to_highlight = "name"


FamilyAdmin.highlight_deleted_field.short_description = FamilyAdmin.field_to_highlight
admin.site.register(Family, FamilyAdmin)
