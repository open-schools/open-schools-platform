from django.db.models import Q
from django_filters import rest_framework as filters

from open_schools_platform.marketplace_management.models import App


class AppFilterset(filters.FilterSet):
    category_id = filters.NumberFilter("category_id")
    type = filters.ChoiceFilter(field_name="type", choices=App.APP_TYPES)
    q = filters.CharFilter(method="filter_q")

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = App
        fields = [
            "category_id",
            "developer_profile_id",
        ]
