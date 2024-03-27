from rest_framework.exceptions import ValidationError


def only_true_value(value: bool):
    if not value:
        raise ValidationError("You can use only true value there")
