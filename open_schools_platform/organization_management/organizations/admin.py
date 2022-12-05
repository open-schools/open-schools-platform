from open_schools_platform.common.admin import InputFilter, BaseAdmin, admin_wrapper
from open_schools_platform.organization_management.organizations.models import Organization
from django.utils.translation import gettext_lazy as _

from open_schools_platform.organization_management.organizations.selectors import get_organizations


class INNFilter(InputFilter):
    parameter_name = 'inn'
    title = _('INN')

    def queryset(self, request, queryset):
        if self.value() is not None:
            inn = self.value()

            return get_organizations(filters={"inn": inn})


@admin_wrapper(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ("inn", "id")
    search_fields = ("name",)
    list_filter = (INNFilter,)
