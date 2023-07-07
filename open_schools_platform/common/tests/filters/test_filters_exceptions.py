from django.test import TestCase

from open_schools_platform.testing.selectors import get_test_model_objects
from rest_framework.exceptions import ValidationError


class OrSearchExceptionsTest(TestCase):
    def test_completely_invalid_format(self):
        filters = {
            "or_search": "test"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_no_square_brackets(self):
        filters = {
            "or_search": "value:fil1,fil2"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_no_colon(self):
        filters = {
            "or_search": "value[fil1,fil2]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_space_in_filters_list(self):
        filters = {
            "or_search": "value:[fil1, fil2]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_filter_is_not_listed_in_filterset(self):
        filters = {
            "or_search": "value:[char_filter,test_test_test]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_invalid_filter_format(self):
        filters = {
            "or_search": "value:[char_filter,integer_filter]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_filter_has_method(self):
        filters = {
            "or_search": "value:[char_filter,filter_with_method]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))

    def test_filter_has_lookup_expr_that_is_not_allowed(self):
        filters = {
            "or_search": "value:[char_filter,filter_with_redefined_lookup_expr]"
        }
        self.assertRaises(ValidationError, lambda: get_test_model_objects(filters=filters))
