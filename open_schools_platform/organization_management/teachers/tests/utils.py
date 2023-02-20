from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.teachers.models import TeacherProfile, Teacher
from open_schools_platform.organization_management.teachers.services import create_teacher, add_teacher_to_circle


def create_test_teacher(circle: Circle, teacher_profile: TeacherProfile) -> Teacher:
    return create_teacher(name="test_teacher", circle=circle, teacher_profile=teacher_profile)


def create_teacher_and_add_to_circle(i: int, circle: Circle) -> Teacher:
    teacher = create_teacher(name=f"test_teacher{i}")
    add_teacher_to_circle(teacher=teacher, circle=circle)

    return teacher
