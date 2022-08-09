from django.contrib import admin
from django.db.models import Q

from .models import Circle
from ...common.admin import InputFilter
from django.utils.translation import gettext_lazy as _


class OrganizationFilter(InputFilter):
    parameter_name = 'organization'
    title = _('organization')

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()

            return queryset.filter(
                Q(organization__name__icontains=name)
            )


class AddressFilter(InputFilter):
    parameter_name = 'address'
    title = _('address')

    def queryset(self, request, queryset):
        if self.value() is not None:
            address = self.value()

            return queryset.filter(
                Q(address__icontains=address)
            )


class CircleAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "address", "capacity", "id")
    search_fields = ("name",)
    list_filter = (OrganizationFilter, AddressFilter)


admin.site.register(Circle, CircleAdmin)
