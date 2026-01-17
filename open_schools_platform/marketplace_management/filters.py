from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters import UUIDFilter

from open_schools_platform.marketplace_management.models import App, AppType
from open_schools_platform.marketplace_management.models import Installation


class AppFilterset(filters.FilterSet):
    SORT_CHOICES = (
        ("newest", "Newest"),
        # ("rating", "Rating"),
        # ("popular", "Popular"),
        ("relevance", "Relevance"),
    )

    sort = filters.ChoiceFilter(method="filter_sort", choices=SORT_CHOICES)
    category_id = filters.NumberFilter("category_id")
    type = filters.ChoiceFilter(field_name="type", choices=AppType.choices)
    q = filters.CharFilter(method="filter_q")

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_sort(self, queryset, name, value):
        if value == "newest":
            return queryset.order_by("-updated_at")
        elif value == "relevance":
            return queryset.order_by("-updated_at")
        else:
            return queryset

    class Meta:
        model = App
        fields = [
            "category_id",
            "developer_profile_id",
        ]


class InstallationFilterset(filters.FilterSet):
    organization_id = UUIDFilter(field_name="organization__id", lookup_expr="exact")
    app_id = UUIDFilter(field_name="app__id", lookup_expr="exact")
    status = filters.BooleanFilter(field_name="active")

    class Meta:
        model = Installation
        fields = ["organization_id", "app_id", "status"]
