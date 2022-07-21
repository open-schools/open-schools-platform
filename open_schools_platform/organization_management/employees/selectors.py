from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.organization_management.employees.filters import EmployeeFilter, EmployeeProfileFilter
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.user_management.users.models import User


def get_employee(*, filters=None, user: User = None) -> Employee:
    filters = filters or {}

    qs = Employee.objects.all()
    employee = EmployeeFilter(filters, qs).qs.first()

    if user and employee and not user.has_perm("employees.employee_access", employee):
        raise PermissionDenied

    return employee


def get_employees(*, filters=None, user: User = None) -> QuerySet:
    filters = filters or {}

    qs = Employee.objects.all()
    employees = EmployeeFilter(filters, qs).qs

    if user and not user.has_perm("employees.employee_list_access", filters):
        raise PermissionDenied

    return employees


def get_employee_profile(*, filters=None, user: User = None) -> EmployeeProfile:
    filters = filters or {}

    qs = EmployeeProfile.objects.all()
    employee_profile = EmployeeProfileFilter(filters, qs).qs.first()

    if user and employee_profile and not user.has_perm("employees.employee_profile_access", employee_profile):
        raise PermissionDenied

    return employee_profile
