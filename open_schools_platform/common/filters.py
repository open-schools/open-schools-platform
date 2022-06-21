import django_filters
from django.db.models import Q
from django_filters import CharFilter
from rest_framework.exceptions import ValidationError


class BaseFilterSet(django_filters.FilterSet):
    """
    BaseFilterSet provide you some useful features:

    1. Opportunity to use special field OR_SEARCH_FIELD that will search
    for all char fields and combine results
        * This feature works only if your input dictionary has  pair [OR_SEARCH_FIELD: some_value]
    2. Will raise ValidationError when filter get not valid data
    3. Will order result by "-created_at" field
        * To use this class your input model type should inherit BaseModel
        otherwise you can redefine ORDER_FIELD
        * To disable this feature write ORDER_FIELD=None
        * Note: symbol '-' is the reverse trigger
    """
    OR_SEARCH_FIELD = "search"
    ORDER_FIELD = "-created_at"

    def __init__(self, *args, **kwargs):
        self.search_value = None
        super().__init__(*args, **kwargs)
        if not self.is_valid():
            raise ValidationError(self.errors)

    def OR(self, queryset, field_name, value):
        if type(value) is not str:
            raise ValidationError(detail="Search field must be str type.")

        self.search_value = value
        return queryset

    @property
    def qs(self):
        base_queryset = super().qs
        if self.ORDER_FIELD:
            base_queryset = base_queryset.order_by(self.ORDER_FIELD)

        if not self.search_value:
            return base_queryset

        query = Q()
        filters = self.get_filters()
        for filter in filters.values():
            if type(filter) is CharFilter and filter.field_name != self.OR_SEARCH_FIELD:
                query |= Q(**{"{0}__icontains".format(filter.field_name): self.search_value})

        return base_queryset.filter(query)
