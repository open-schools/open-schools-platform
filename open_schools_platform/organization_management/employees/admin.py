from django.contrib import admin

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile

admin.site.register(Employee)
admin.site.register(EmployeeProfile)
