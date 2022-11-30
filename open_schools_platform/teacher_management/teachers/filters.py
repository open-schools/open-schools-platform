from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.teacher_management.teachers.models import Teacher


class TeacherFilter(BaseFilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    phone = CharFilter(field_name="teacher_profile__phone")
    circle_name = CharFilter(field_name="circle__name", lookup_expr="icontains")

    class Meta:
        model = Teacher
        fields = ("circle", "teacher_profile", "id")
