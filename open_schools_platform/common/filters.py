import django_filters
from rest_framework.exceptions import ValidationError


class BaseFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_valid():
            raise ValidationError(self.errors)
