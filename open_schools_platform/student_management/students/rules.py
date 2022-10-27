import rules

from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


@rules.predicate
def is_student_profile_owner(user: User, student_profile: StudentProfile):
    return user and student_profile.user == user


@rules.predicate
def has_family_with_this_student_profile(user: User, student_profile: StudentProfile):
    return get_family(filters={"student_profiles": str(student_profile.id),
                               "parent_profiles": str(user.parent_profile.id)}) is not None


rules.add_perm("students.student_profile_access", is_student_profile_owner | has_family_with_this_student_profile)
