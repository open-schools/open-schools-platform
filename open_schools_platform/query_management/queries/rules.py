import rules

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


@rules.predicate
def employee_profile_or_organization_access(user: User, query: Query):
    if type(query.sender) == Organization and type(query.recipient) == EmployeeProfile:
        return user.has_perm("organizations.organization_access", query.sender) or \
               user.has_perm("employees.employee_profile_access", query.recipient)
    return False


@rules.predicate
def student_profile_or_circle_access(user: User, query: Query):
    if type(query.sender) == StudentProfile and type(query.recipient) == Circle:
        return user.has_perm("students.student_profile_access", query.sender) or \
               user.has_perm("circles.circle_access", query.recipient)
    return False


rules.add_perm("queries.query_access", employee_profile_or_organization_access | student_profile_or_circle_access)
