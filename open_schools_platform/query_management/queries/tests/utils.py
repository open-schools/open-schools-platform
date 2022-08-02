from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.services import create_student
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.tests.utils import create_test_user


def create_test_student_join_circle_query(user: User = None, circle: Circle = None) -> Query:
    if user is None:
        user = create_test_user(phone="+79021111111")
    if circle is None:
        circle = create_test_circle()
    student = create_student(name='test_student')
    query = create_query(
        sender_model_name="studentprofile", sender_id=user.student_profile.id,
        recipient_model_name="circle", recipient_id=circle.id,
        body_model_name="student", body_id=student.id
    )
    return query


def change_test_query_status(query: Query, new_status: str) -> Query:
    query.status = new_status
    query.save()
    return query
