from typing import List, Dict, Any

from django.test import TestCase
from open_schools_platform.testing.selectors import get_test_model_objects
from open_schools_platform.testing.tests.utils import create_test_model_objects


def get_test_model_results_from_qs(qs):
    return list(map(lambda test_object: test_object.integer_field, qs))


class OrSearchTests(TestCase):
    def setUp(self):
        self.test_model_data_payloads = [
            {
                "char_field": "Test1",
                "integer_field": 1
            },
            {
                "char_field": "test2",
                "integer_field": 2
            },
            {
                "char_field": "another_string",
                "second_char_field": "test3",
                "integer_field": 3
            },
            {
                "char_field": "another_string",
                "char_field_with_choices": "FIRST",
                "integer_field": 4
            },
            {
                "char_field": "colon:space space",
                "integer_field": 5
            }
        ]

        self.test_model_objects = create_test_model_objects(data_list=self.test_model_data_payloads)

    def get_test_objects_test(self, correct_answers: List[int], filters: Dict[str, Any]):
        result = get_test_model_objects(filters=filters)
        self.assertCountEqual(correct_answers, get_test_model_results_from_qs(result))

    def test_successfully_works_with_one_filter(self):
        correct_answers = [1, 2]
        filters = {
            "or_search": "test:[char_filter]"
        }

        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_several_filters(self):
        correct_answers = [1, 2, 3]
        filters = {
            "or_search": "test:[char_filter,second_char_filter]"
        }
        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_ChoiceFilter(self):
        correct_answers = [4]
        filters = {
            "or_search": "first:[char_filter,choice_filter]"
        }
        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_AllValuesFilter(self):
        correct_answers = [4]
        filters = {
            "or_search": "first:[char_filter,all_values_filter]"
        }
        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_other_filters(self):
        correct_answers = [3]
        filters = {
            "or_search": "test:[char_filter,second_char_filter]",
            "integer_filter": 3
        }
        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_filters_that_were_already_used_with_or_search(self):
        correct_answers = [3]
        filters = {
            "or_search": "test:[char_filter,second_char_filter]",
            "char_filter": "another_string"
        }
        self.get_test_objects_test(correct_answers, filters)

    def test_successfully_works_with_spaces_and_colons_in_filtering_value(self):
        correct_answers = [5]
        filters = {
            "or_search": "colon:space space:[char_filter]"
        }
        self.get_test_objects_test(correct_answers, filters)
