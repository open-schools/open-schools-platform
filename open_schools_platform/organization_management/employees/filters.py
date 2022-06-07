from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.employees.models import Employee


class EmployeeFilter(BaseFilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    position = CharFilter(field_name="position", lookup_expr="icontains")
    phone = CharFilter(field_name="user__phone", lookup_expr="icontains")

    class Meta:
        model = Employee
        fields = ('user', 'organization')
