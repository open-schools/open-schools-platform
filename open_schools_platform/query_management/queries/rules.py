import rules

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.ticket_management.tickets.rules import ticket_sender_access, ticket_recipient_access

access_name = {
    Organization: 'organizations.organization_access',
    EmployeeProfile: 'employees.employeeprofile_access',
    StudentProfile: 'students.studentprofile_access',
    Circle: 'circles.circle_access',
    Family: 'families.family_access',
    ParentProfile: 'parents.parentprofile_access',
    TeacherProfile: 'teachers.teacherprofile_access'
}


@rules.predicate
def has_sender_or_recipient_access(user, query):
    sender_access_name = access_name[type(query.sender)]
    recipient_access_name = access_name[type(query.recipient)]
    return user.has_perm(sender_access_name, query.sender) or user.has_perm(recipient_access_name, query.recipient)


rules.add_perm("queries.query_access", has_sender_or_recipient_access |
               ticket_sender_access() | ticket_recipient_access())
