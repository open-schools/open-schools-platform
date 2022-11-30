import uuid

from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.exceptions import NotAcceptable, MethodNotAllowed

from open_schools_platform.common.services import model_update, BaseQueryHandler
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.photo_management.photos.services import create_photo
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
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


class TeacherProfileQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                        Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(TeacherProfileQueryHandler, query, new_status, user)

        circle_access = user.has_perm("circles.circle_access", query.recipient)
        teacher_profile_access = user.has_perm("teachers.teacher_profile_access", query.sender)

        if teacher_profile_access and circle_access:
            pass
        elif teacher_profile_access:
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")
            if new_status != Query.Status.CANCELED:
                raise NotAcceptable("User can only set canceled status")
        elif circle_access:
            if new_status == Query.Status.CANCELED:
                raise NotAcceptable("Circle cannot cancel query, it can only decline it")
            if query.status == Query.Status.CANCELED:
                raise NotAcceptable("Сan no longer change the query")

        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise MethodNotAllowed("put", detail="Query is corrupted")
            query.body.circle = query.recipient
            query.body.teacher_profile = query.sender
            query.body.save()

        return query

    setattr(TeacherProfile, "query_handler", query_handler)
