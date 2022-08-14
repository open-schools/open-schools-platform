from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.query_management.queries.filters import QueryFilterByStatus
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_model


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    address = CharFilter(field_name="address", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")

    class Meta:
        model = Circle
        fields = ("id", "organization", "name", "capacity", "description")


class StudentQueryFilter(QueryFilterByStatus):
    name = CharFilter(method='student_profile_name_filter')

    def student_profile_name_filter(self, queryset, name, value):
        query_list = list(filter(lambda query: value in get_model(query.body_ct, query.body_id).name, queryset))
        query_ids_list = list(map(lambda query: query.id, query_list))
        return Query.objects.filter(pk__in=query_ids_list)
