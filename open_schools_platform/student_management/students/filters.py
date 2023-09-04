from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter, filter_by_ids, MetaCharIContainsMixin
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile, Student


def parent_phone_filter(queryset, field_name, value):
    ids = []
    parent_profiles = ParentProfile.objects.prefetch_related('families') \
        .filter(user__phone__icontains=value)
    families = Family.objects.none()

    for i in parent_profiles:
        families |= i.families.all()

    for i in queryset:
        if i.student_profile.families.all() & families:
            ids.append(str(i.student_profile.id))
            continue

    return queryset.filter(student_profile__id__in=ids)


def parent_name_filter(queryset, field_name, value):
    ids = []
    parent_profiles = ParentProfile.objects.prefetch_related('families') \
        .filter(user__parent_profile__name__icontains=value)
    families = Family.objects.none()

    for i in parent_profiles:
        families |= i.families.all()

    for i in queryset:
        if i.student_profile.families.all() & families:
            ids.append(str(i.student_profile.id))
            continue

    return queryset.filter(student_profile__id__in=ids)


class StudentProfileFilter(BaseFilterSet):
    families = UUIDInFilter(field_name="families", lookup_expr="in")
    ids = CharFilter(method=filter_by_ids)
    or_search = CharFilter(field_name="or_search", method="OR")

    class Meta(MetaCharIContainsMixin):
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age', 'phone', 'photo')


class StudentFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")
    parent_phone = CharFilter(field_name="parent_phone", method=parent_phone_filter)
    parent_name = CharFilter(field_name="parent_name", method=parent_name_filter)

    class Meta(MetaCharIContainsMixin):
        model = Student
        fields = ('id', 'name', 'circle', 'student_profile', 'student_profile__phone',
                  'circle__name', 'student_profile__name', "circle__organization",
                  "parent_phone", "parent_name")
