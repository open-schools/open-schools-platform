from open_schools_platform.testing.models import TestModel


def create_test_model(char_field: str = None, second_char_field: str = None,
                      char_field_with_choices: TestModel.Variants = None, integer_field: int = None) -> TestModel:
    test_model = TestModel.objects.create(
        char_field=char_field,
        second_char_field=second_char_field,
        char_field_with_choices=char_field_with_choices,
        integer_field=integer_field
    )
    return test_model
