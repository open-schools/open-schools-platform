from django.contrib import admin
from django.db.models import Q

from open_schools_platform.common.admin import InputFilter
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from django.utils.translation import gettext_lazy as _


class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "id")


class OrganizationFilter(InputFilter):
    parameter_name = 'organization'
    title = _('organization')

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()

            return queryset.filter(
                Q(organization__name__icontains=name)
            )


class EmployeeProfileFilter(InputFilter):
    parameter_name = 'employee_profile'
    title = _('employee profile')

    def queryset(self, request, queryset):
        if self.value() is not None:
            employee_profile = self.value()

            return queryset.filter(
                Q(employee_profile__user__phone=employee_profile)
            )


class PositionFilter(InputFilter):
    parameter_name = 'position'
    title = _('position')

    def queryset(self, request, queryset):
        if self.value() is not None:
            position = self.value()

            return queryset.filter(
                Q(position__icontains=position)
            )


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "employee_profile", "organization", "id")
    search_fields = ("name",)
    list_filter = (OrganizationFilter, EmployeeProfileFilter, PositionFilter)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeProfile, EmployeeProfileAdmin)
