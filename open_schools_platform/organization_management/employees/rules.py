import rules

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_common_organization(user: User, employee: Employee):
    return employee.organization in get_organizations_by_user(user)


@rules.predicate
def is_filtering_employees_in_common_organization(user: User, filters):
    user_organizations = get_organizations_by_user(user)
    if not user_organizations:
        return False
    return filters.get("organization") in list(map(lambda x: x.id, list(user_organizations)))


@rules.predicate
def is_employee_profile_owner(user: User, employee_profile: EmployeeProfile):
    return employee_profile.user == user


rules.add_perm("employees.employee_access", has_common_organization)
rules.add_perm("employees.employee_list_access", is_filtering_employees_in_common_organization)
rules.add_perm("employees.employee_profile_access", is_employee_profile_owner)
