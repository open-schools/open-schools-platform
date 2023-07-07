from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


class EmployeeFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")
    name = CharFilter(field_name="name", lookup_expr="icontains")
    position = CharFilter(field_name="position", lookup_expr="icontains")
    phone = CharFilter(field_name="employee_profile__user__phone", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")

    class Meta:
        model = Employee
        fields = ("organization", "employee_profile", "id")


class EmployeeProfileFilter(BaseFilterSet):
    phone = CharFilter(field_name="user__phone", lookup_expr="exact")

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'user')
