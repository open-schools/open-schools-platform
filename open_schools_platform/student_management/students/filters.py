from typing import List

import django_filters
from django.db.models import CharField
from django_filters import BooleanFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.student_management.students.models import StudentProfile, Student


class StudentProfileFilter(BaseFilterSet):
    not_deleted = BooleanFilter(field_name="deleted", lookup_expr="isnull")

    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age', 'phone', 'photo')


class StudentFilter(BaseFilterSet):
    not_deleted = BooleanFilter(field_name="deleted", lookup_expr="isnull")

    @staticmethod
    def get_swagger_filters(prefix: str = "", include: List[str] = None):
        if include is None:
            include = []

        if not include:
            include = ["name", "id", "circle", "student_profile",
                       "student_profile__phone", "circle__name", "circle__organization"]
        return BaseFilterSet.get_dict_filters(StudentFilter, prefix, include)

    class Meta:
        model = Student
        fields = ('id', 'name', 'circle', 'student_profile', 'student_profile__phone',
                  'circle__name', 'student_profile__name', "circle__organization")
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
