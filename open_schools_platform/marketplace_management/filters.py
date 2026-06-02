from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters import UUIDFilter

from open_schools_platform.marketplace_management.models import App
from open_schools_platform.marketplace_management.models import Installation


class AppFilterset(filters.FilterSet):
    SORT_CHOICES = (
        ("newest", "Newest"),
        ("relevance", "Relevance"),
    )

    sort = filters.ChoiceFilter(method="filter_sort", choices=SORT_CHOICES)
    category_id = filters.NumberFilter("category_id")
    q = filters.CharFilter(method="filter_q")

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_sort(self, queryset, name, value):
        if value in ("newest", "relevance"):
            return queryset.order_by("-updated_at")
        return queryset

    class Meta:
        model = App
        fields = [
            "category_id",
        ]


class InstallationFilterset(filters.FilterSet):
    schoolId = UUIDFilter(field_name="organization__id", lookup_expr="exact")
    appId = UUIDFilter(field_name="app__id", lookup_expr="exact")
    status = filters.BooleanFilter(field_name="active")

    class Meta:
        model = Installation
        fields = ["schoolId", "appId", "status"]