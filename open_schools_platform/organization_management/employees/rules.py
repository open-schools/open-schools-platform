import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_common_organization(user: User, employee: Employee):
    return employee.organization in get_organizations_by_user(user)


@rules.predicate
@predicate_input_type_check
def is_employee_profile_owner(user: User, employee_profile: EmployeeProfile):
    return employee_profile.user == user


rules.add_perm("employees.employee_access", has_common_organization)
rules.add_perm("employees.employee_profile_access", is_employee_profile_owner)
