import rules

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
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


@rules.predicate
def parent_profile_or_family_access(user: User, query: Query):
    if type(query.sender) == Family and type(query.recipient) == ParentProfile:
        return user.has_perm("parents.parent_profile_access", query.recipient) or \
               user.has_perm("families.family_access", query.sender)
    return False


@rules.predicate
def circle_or_family_access(user: User, query: Query):
    if type(query.sender) == Circle and type(query.recipient) == Family:
        return user.has_perm("families.family_access", query.recipient) or \
               user.has_perm("circles.circle_access", query.sender)
    return False


@rules.predicate
def teacher_profile_access(user: User, query: Query):
    if type(query.sender) == Circle and type(query.recipient) == TeacherProfile:
        return user.has_perm("teachers.teacher_profile_access", query.recipient) or \
               user.has_perm("circles.circle_access", query.sender)


rules.add_perm("queries.query_access", employee_profile_or_organization_access | student_profile_or_circle_access |
               parent_profile_or_family_access | circle_or_family_access | teacher_profile_access)
