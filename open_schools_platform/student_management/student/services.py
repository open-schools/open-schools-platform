from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
    )
    return student_profile


def can_user_create_student_profile_check(family: Family, user: User) -> bool:
    # TODO:  think about mypy check hidden attributes made by related_name
    return user.parent_profile in family.parent_profiles.all()  # type: ignore
