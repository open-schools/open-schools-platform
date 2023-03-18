import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.organization_management.teachers.models import TeacherProfile, Teacher
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def is_teacher_profile_owner(user: User, teacher_profile: TeacherProfile):
    return teacher_profile.user == user


@rules.predicate
def is_teacher_owner(user: User, teacher: Teacher):
    return is_teacher_profile_owner(user, teacher.teacher_profile)


@rules.predicate
def has_access_for_circle(user: User, teacher: Teacher):
    return user.has_perm("circles.circle_access", teacher.circle)


rules.add_perm("teachers.teacher_profile_access", is_teacher_profile_owner)
rules.add_perm("teachers.teacher_access", is_teacher_owner | has_access_for_circle)
