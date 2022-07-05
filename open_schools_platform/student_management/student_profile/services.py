from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.student_management.student_profile.models import StudentProfile
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
    )
    return student_profile


def can_user_create_student_profile_check(family_parent_profiles: Family.parent_profiles, user: User) -> bool:
    return user.parent_profile in family_parent_profiles
