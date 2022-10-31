from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.parent_management.families.services import create_family, add_student_profile_to_family
from open_schools_platform.student_management.students.models import StudentProfile, Student
from open_schools_platform.student_management.students.services import create_student, create_student_profile
from open_schools_platform.user_management.users.models import User


def get_deleted_student_profiles():
    student_profiles = StudentProfile.objects.all(force_visibility=True).filter(deleted__isnull=False)
    return student_profiles


def get_deleted_students():
    students = Student.objects.all(force_visibility=True).filter(deleted__isnull=False)
    return students


def create_test_student(circle: Circle = None, student_profile: StudentProfile = None):
    student = create_student("test_student", circle=circle, student_profile=student_profile)
    return student


def create_test_student_with_user_in_organization(user: User):
    circle = create_test_circle_with_user_in_org(user)
    student_profile = create_student_profile("test_st_profile", 12)
    student = create_student(name="test_student1", circle=circle, student_profile=student_profile)
    return student


def create_test_student_with_user_in_parental_status(user: User):
    family = create_family(user.parent_profile, name="test_family")
    student_profile = create_student_profile("test_st_profile", 12)
    add_student_profile_to_family(family, student_profile)
    student = create_student(name="test_student1", student_profile=student_profile)
    return student
