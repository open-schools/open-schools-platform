from django_filters import CharFilter, NumberFilter, ChoiceFilter, AllValuesFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.testing.models import TestModel


class TestModelFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")
    char_filter = CharFilter(field_name="char_field")
    second_char_filter = CharFilter(field_name="second_char_field")
    choice_filter = ChoiceFilter(field_name="char_field_with_choices", choices=TestModel.Variants.choices)
    all_values_filter = AllValuesFilter(field_name="char_field_with_choices")
    integer_filter = NumberFilter(field_name="integer_field")
    filter_with_redefined_lookup_expr = CharFilter(field_name="char_field", lookup_expr="in")
    filter_with_method = CharFilter(method="test_method")

    def test_method(self, queryset, name, value):
        pass
