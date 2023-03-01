import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.student_management.students.models import StudentProfile, Student
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def is_student_profile_owner(user: User, student_profile: StudentProfile):
    return student_profile.user == user


@rules.predicate
@predicate_input_type_check
def has_family_with_this_student_profile(user: User, student_profile: StudentProfile):
    return get_family(filters={"student_profiles": str(student_profile.id),
                               "parent_profiles": str(user.parent_profile.id)}) is not None


@rules.predicate
def is_student_owner(user: User, student: Student):
    return is_student_profile_owner(user, student.student_profile)


@rules.predicate
def is_parent_for_student(user: User, student: Student):
    return has_family_with_this_student_profile(user, student.student_profile)


@rules.predicate
def has_access_for_circle(user: User, student: Student):
    return user.has_perm("circles.circle_access", student.circle)


rules.add_perm("students.student_profile_access", is_student_profile_owner | has_family_with_this_student_profile)
rules.add_perm("students.student_access", is_student_owner | is_parent_for_student | has_access_for_circle)
