import django_filters
from django.db.models import Q
from django_filters import CharFilter
from rest_framework.exceptions import ValidationError

OR_SEARCH_FIELD = "search"


class BaseFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        self.search_value = None
        super().__init__(*args, **kwargs)
        if not self.is_valid():
            raise ValidationError(self.errors)

    def OR(self, queryset, field_name, value):
        self.search_value = value
        return queryset

    @property
    def qs(self):
        base_queryset = super().qs

        if not self.search_value:
            return base_queryset

        query = Q()
        filters = self.get_filters()
        for key in self.get_fields():
            if type(filters[key]) is CharFilter:
                query |= Q(**{"{0}__icontains".format(key): self.search_value})

        return base_queryset.filter(query)
