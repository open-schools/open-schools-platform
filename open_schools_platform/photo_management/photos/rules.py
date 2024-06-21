import rules

from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_studentprofile_access(user: User, photo: Photo):
    student_profile = StudentProfile.objects.filter(photo=photo.id).first()
    return student_profile and user.has_perm('students.studentprofile_access', student_profile)


@rules.predicate
def has_teacherprofile_access(user: User, photo: Photo):
    teacher_profile = TeacherProfile.objects.filter(photo=photo.id).first()
    return teacher_profile and user.has_perm('teachers.teacherprofile_access', teacher_profile)


rules.add_perm("photos.photo_access", has_studentprofile_access | has_teacherprofile_access)
