import rules

from open_schools_platform.common.rules import predicate_input_type_check, has_related_organization
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_common_organization(user: User, employee: Employee):
    return has_related_organization(user, employee.organization)


@rules.predicate
@predicate_input_type_check
def is_employee_profile_owner(user: User, employee_profile: EmployeeProfile):
    return employee_profile.user == user


rules.add_perm("employees.employee_access", has_common_organization)
rules.add_perm("employees.employeeprofile_access", is_employee_profile_owner)
