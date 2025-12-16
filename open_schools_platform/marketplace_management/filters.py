from django.db.models import Q
from django_filters import rest_framework as filters

from open_schools_platform.marketplace_management.models import App


class AppFilterset(filters.FilterSet):
    SORT_CHOICES = (
        ("newest", "Newest"),
        # ("rating", "Rating"),
        # ("popular", "Popular"),
        ("relevance", "Relevance"),
    )

    sort = filters.ChoiceFilter(method="filter_sort", choices=SORT_CHOICES)
    category_id = filters.NumberFilter("category_id")
    type = filters.ChoiceFilter(field_name="type", choices=App.APP_TYPES)
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
