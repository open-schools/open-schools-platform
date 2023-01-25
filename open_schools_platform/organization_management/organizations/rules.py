import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.organization_management.employees.selectors import get_employee
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def is_in_organization(user: User, organization: Organization):
    return get_employee(filters={"employee_profile": user.employee_profile,
                                 "organization": organization}) is not None


@rules.predicate
def is_filtering_own_organizations(user: User, filters):
    return filters.get("employee_profile") == user.employee_profile.id


rules.add_perm("organizations.organization_access", is_in_organization)
rules.add_perm("organizations.organization_list_access", is_filtering_own_organizations)
