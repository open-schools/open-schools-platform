from typing import List

import django_filters
from django.db.models import CharField
from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.student_management.students.models import StudentProfile, Student


class StudentProfileFilter(BaseFilterSet):
    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age')


class StudentFilter(BaseFilterSet):
    circle_name = CharFilter(field_name='circle__name', lookup_expr='icontains')
    student_profile_name = CharFilter(field_name='student_profile__name', lookup_expr='icontains')

    @staticmethod
    def get_swagger_filters(prefix: str = "", include: List[str] = []):
        if not include:
            include = ["name", "id", "id", "circle", "student_profile", "circle_name", "student_profile_name"]
        return BaseFilterSet.get_dict_filters(StudentFilter, prefix, include)

    class Meta:
        model = Student
        fields = ('id', 'name', 'circle', 'student_profile')
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
