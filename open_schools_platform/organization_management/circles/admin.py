from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter

from .models import Circle
from .selectors import get_circles
from ...common.admin import InputFilter
from django.utils.translation import gettext_lazy as _

from ...common.models import DeleteAdmin


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


class CircleAdmin(DeleteAdmin, LeafletGeoAdmin):
    list_display = DeleteAdmin.list_display + ("organization", "address", "capacity",
                                               "location", "id")
    search_fields = ("name",)
    list_filter = DeleteAdmin.list_filter + (OrganizationFilter, AddressFilter)


DeleteAdmin.init_model(CircleAdmin)

admin.site.register(Circle, CircleAdmin)
