from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
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


def update_student_profile(*, student_profile: StudentProfile, data) -> StudentProfile:
    non_side_effect_fields = ['age', 'name']
    filtered_data = filter_dict_from_none_values(data)
    student_profile, has_updated = model_update(
        instance=student_profile,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return student_profile
