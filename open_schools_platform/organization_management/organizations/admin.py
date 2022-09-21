from django.contrib import admin
from open_schools_platform.common.admin import InputFilter
from open_schools_platform.organization_management.organizations.models import Organization
from django.utils.translation import gettext_lazy as _

from open_schools_platform.organization_management.organizations.selectors import get_organizations
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter


class INNFilter(InputFilter):
    parameter_name = 'inn'
    title = _('INN')

    def queryset(self, request, queryset):
        if self.value() is not None:
            inn = self.value()

            return get_organizations(filters={"inn": inn})


class OrganizationAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field", "inn", "id") + SafeDeleteAdmin.list_display
    search_fields = ("name",)
    list_filter = (INNFilter, SafeDeleteAdminFilter) + SafeDeleteAdmin.list_filter

    field_to_highlight = "name"


OrganizationAdmin.highlight_deleted_field.short_description = OrganizationAdmin.field_to_highlight

admin.site.register(Organization, OrganizationAdmin)
