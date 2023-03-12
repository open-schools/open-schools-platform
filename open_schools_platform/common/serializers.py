from collections import OrderedDict

from rest_framework.fields import CharField, DictField, ChoiceField, ListField
from rest_framework.serializers import Serializer

from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.errors.codes import error_codes


def get_serializer_with_fields(serializer, fields):
    """
    Returns a new serializer with the specified fields.
    """

    class NewSerializer(serializer):
        def __init__(self, *args, **kwargs):
            # Don't pass the 'fields' arg up to the superclass
            fields = kwargs.pop('fields', None)
            NewSerializer.__name__ = f"Partial{serializer.__name__}"
            # Instantiate the superclass normally
            super(NewSerializer, self).__init__(*args, **kwargs)

            if fields is not None:
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields)
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

    return NewSerializer(fields=fields)


class ErrorSerializer(Serializer):
    code = ChoiceField(required=False,
                       choices=[item.__name__ for sublist in error_codes.values() for item in sublist])
    message = CharField(required=False, max_length=25, allow_null=True)
    violation_fields = DictField(required=False, allow_null=True, child=ListField(child=CharField()))
    violations = ListField(required=False, child=CharField())

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict(filter_dict_from_none_values(result))


class Error400Serializer(ErrorSerializer):
    code = ChoiceField(required=False, choices=list(map(lambda cls: cls.__name__, error_codes[400])))


class Error401Serializer(ErrorSerializer):
    code = ChoiceField(required=False, choices=list(map(lambda cls: cls.__name__, error_codes[401])))
