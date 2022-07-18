from django.db.models import QuerySet

from open_schools_platform.organization_management.employees.filters import EmployeeFilter, EmployeeProfileFilter
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


def get_employee(*, filters=None) -> Employee:
    filters = filters or {}

    qs = Employee.objects.all()

    return EmployeeFilter(filters, qs).qs.first()


def get_employees(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Employee.objects.all()

    return EmployeeFilter(filters, qs).qs


def get_employee_profile(*, filters=None) -> EmployeeProfile:
    filters = filters or {}

    qs = EmployeeProfile.objects.all()

    return EmployeeProfileFilter(filters, qs).qs.first()
