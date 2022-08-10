from django.contrib import admin
from .models import Circle
from .selectors import get_circles
from ...common.admin import InputFilter
from django.utils.translation import gettext_lazy as _


class OrganizationFilter(InputFilter):
    parameter_name = 'organization_name'
    title = _('organization name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            organization = self.value()

            return get_circles(filters={"organization_name": organization})


class AddressFilter(InputFilter):
    parameter_name = 'address'
    title = _('address')

    def queryset(self, request, queryset):
        if self.value() is not None:
            address = self.value()
            return get_circles(filters={"address": address})


class CircleAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "address", "capacity", "id")
    search_fields = ("name",)
    list_filter = (OrganizationFilter, AddressFilter)


admin.site.register(Circle, CircleAdmin)
