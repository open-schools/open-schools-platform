from django.contrib import admin
from django.db.models import Q

from open_schools_platform.common.admin import InputFilter
from open_schools_platform.organization_management.organizations.models import Organization
from django.utils.translation import gettext_lazy as _


class INNFilter(InputFilter):
    parameter_name = 'inn'
    title = _('INN')

    def queryset(self, request, queryset):
        if self.value() is not None:
            inn = self.value()

            return queryset.filter(
                Q(inn=inn)
            )


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "inn", "id")
    search_fields = ("name",)
    list_filter = (INNFilter,)


admin.site.register(Organization, OrganizationAdmin)
