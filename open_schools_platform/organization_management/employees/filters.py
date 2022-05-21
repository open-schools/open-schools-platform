from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.employees.models import Employee


class EmployeeFilter(BaseFilterSet):
    class Meta:
        model = Employee
        fields = ('user', 'organization')
