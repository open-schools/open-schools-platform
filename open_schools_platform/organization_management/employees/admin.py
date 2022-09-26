from django.contrib import admin
from open_schools_platform.common.admin import InputFilter
from open_schools_platform.common.models import DeleteAdmin
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from django.utils.translation import gettext_lazy as _

from open_schools_platform.organization_management.employees.selectors import get_employees
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter


class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "id")


class OrganizationFilter(InputFilter):
    parameter_name = 'organization_name'
    title = _('organization name')

    def queryset(self, request, queryset):
        if self.value() is not None:
            organization = self.value()

            return get_employees(filters={"organization_name": organization})


class EmployeeProfileFilter(InputFilter):
    parameter_name = 'employee_profile'
    title = _('employee profile phone')

    def queryset(self, request, queryset):
        if self.value() is not None:
            employee_profile = self.value()

            return get_employees(filters={"phone": employee_profile})


class PositionFilter(InputFilter):
    parameter_name = 'position'
    title = _('position')

    def queryset(self, request, queryset):
        if self.value() is not None:
            position = self.value()

            return get_employees(filters={"position": position})


class EmployeeAdmin(DeleteAdmin):
    list_display = DeleteAdmin.list_display + ("position", "employee_profile", "organization", "id")
    search_fields = ("name",)
    list_filter = DeleteAdmin.list_filter + (OrganizationFilter, EmployeeProfileFilter, PositionFilter)


DeleteAdmin.init_model(EmployeeAdmin)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeProfile, EmployeeProfileAdmin)
