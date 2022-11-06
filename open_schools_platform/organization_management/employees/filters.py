from django_filters import CharFilter, BooleanFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


class EmployeeFilter(BaseFilterSet):
    search = CharFilter(field_name="search", method="OR")
    name = CharFilter(field_name="name", lookup_expr="icontains")
    position = CharFilter(field_name="position", lookup_expr="icontains")
    phone = CharFilter(field_name="employee_profile__user__phone", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")
    not_deleted = BooleanFilter(field_name="deleted", lookup_expr="isnull")

    class Meta:
        model = Employee
        fields = ("organization", "employee_profile", "id")


class EmployeeProfileFilter(BaseFilterSet):
    phone = CharFilter(field_name="user__phone", lookup_expr="exact")

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'user')
