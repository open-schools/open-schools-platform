import uuid

from phonenumber_field.phonenumber import PhoneNumber

from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.photo_management.photos.services import create_photo
from open_schools_platform.organization_management.teachers.models import TeacherProfile, Teacher
from open_schools_platform.user_management.users.models import User


def create_teacher_profile(name: str, age: int = None, user: User = None,
                           phone: PhoneNumber = None, photo: uuid.UUID = None) -> TeacherProfile:
    if not photo:
        photo = create_photo()
    teacher_profile = TeacherProfile.objects.create_teacher_profile(
        name=name,
        age=age,
        phone=phone,
        photo=photo,
        user=user
    )
    return teacher_profile


def create_teacher(name: str, circle: Circle = None, teacher_profile: TeacherProfile = None) -> Teacher:
    teacher = Teacher.objects.create_teacher(
        name=name,
        circle=circle,
        teacher_profile=teacher_profile
    )
    return teacher


def update_teacher_profile(*, teacher_profile: TeacherProfile, data) -> TeacherProfile:
    non_side_effect_fields = ['age', 'name', 'phone', 'photo']
    filtered_data = filter_dict_from_none_values(data)
    teacher_profile, has_updated = model_update(
        instance=teacher_profile,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return teacher_profile


def add_teacher_to_circle(teacher: Teacher, circle: Circle):
    teacher.circle = circle
    teacher.save()
