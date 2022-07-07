from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
    )
    return student_profile


def can_user_interact_with_student_profile_check(family: Family, user: User) -> bool:
    return user.parent_profile in family.parent_profiles.all()


def update_student_profile(student_profile: StudentProfile, name: str, age: int) -> StudentProfile:
    if name is not None:
        student_profile.name = name
    if age is not None:
        student_profile.age = age
    student_profile.save()
    return student_profile
