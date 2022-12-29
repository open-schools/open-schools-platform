from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.employees.services import create_employee
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.tests.utils import create_test_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.services import create_student, \
    create_studentprofileicrcle_additional, create_student_profile_circle_query
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.tests.utils import create_test_user


def create_test_student_join_circle_query(user: User = None, circle: Circle = None) -> Query:
    if user is None:
        user = create_test_user(phone="+79021111111")
    if circle is None:
        circle = create_test_circle()
    student = create_student(name='test_student')
    additional = create_test_studentprofilecircle_additional(user=user)
    query = create_student_profile_circle_query(student_profile=user.student_profile, student=student,
                                                circle=circle, additional=additional)
    return query


def create_test_studentprofilecircle_additional(*, user: User, text: str = "Please, let me in!"):
    additional = create_studentprofileicrcle_additional(
        text=text,
        parent_phone=user.phone,
        parent_name=user.parent_profile.name
    )
    return additional


def create_test_employee_invite_organization_query(user: User = None,
                                                   organization: Organization = None) -> Query:
    if user is None:
        user = create_test_user(phone="+79021111111")
    if organization is None:
        organization = create_organization(name="test_organization")
    employee = create_employee(name='test_student')
    query = create_query(
        sender_model_name="organization", sender_id=organization.id,
        recipient_model_name="employeeprofile", recipient_id=user.employee_profile.id,
        body_model_name="student", body_id=employee.id
    )
    return query


def create_test_family_invite_parent_query(i: int = 0, family: Family = None, user: User = None) -> Query:
    if user is None:
        user = create_test_user(phone="+79021111111")
    if family is None:
        family = create_test_family(i=1, parent=create_test_user(phone="+79022222222").parent_profile)
    query = create_query(sender_model_name="family", sender_id=family.id,
                         recipient_model_name="parentprofile", recipient_id=user.parent_profile.id)
    return query


def change_test_query_status(query: Query, new_status: str) -> Query:
    query.status = new_status
    query.save()
    return query
