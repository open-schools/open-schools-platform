import rules

from open_schools_platform.organization_management.teachers.selectors import get_teacher_profile
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.student_management.students.selectors import get_student_profile
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_studentprofile_access(user: User, photo: Photo):
    student_profile = get_student_profile(
        filters={'photo': str(photo.id)},
        user=user
    )
    return student_profile and user.has_perm('students.studentprofile_access', student_profile)


@rules.predicate
def has_teacherprofile_access(user: User, photo: Photo):
    teacher_profile = get_teacher_profile(
        filters={'photo': str(photo.id)},
        user=user
    )
    return teacher_profile and user.has_perm('teachers.teacherprofile_access', teacher_profile)


rules.add_perm("photos.photo_access", has_studentprofile_access | has_teacherprofile_access)
