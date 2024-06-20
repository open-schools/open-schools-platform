import rules

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.ticket_management.tickets.rules import ticket_sender_access, ticket_recipient_access

sender_access_name_by_type = {
    Organization: 'organizations.organization_access',
    StudentProfile: 'students.studentprofile_access',
    Circle: 'circles.circle_access',
    Family: 'families.family_access',
}

recipient_access_name_by_type = {
    EmployeeProfile: 'employees.employeeprofile_access',
    Circle: 'circles.circle_access',
    Family: 'families.family_access',
    ParentProfile: 'parents.parentprofile_access',
    TeacherProfile: 'teachers.teacherprofile_access'
}


@rules.predicate
def has_query_sender_access(user, query):
    sender_access_name = sender_access_name_by_type.get(type(query.sender))
    if sender_access_name:
        return user.has_perm(sender_access_name, query.sender)
    return False


@rules.predicate
def has_query_recipient_access(user, query):
    recipient_access_name = recipient_access_name_by_type.get(type(query.recipient))
    if recipient_access_name:
        return user.has_perm(recipient_access_name, query.recipient)
    return False


rules.add_perm("queries.query_access", has_query_sender_access | has_query_recipient_access |
               ticket_sender_access() | ticket_recipient_access())
