import re
from collections import OrderedDict
from typing import Type

from rest_framework import serializers
from rest_framework.fields import CharField, DictField, ChoiceField, ListField
from rest_framework.serializers import Serializer

from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.errors.codes import error_codes


def partial_serializer_name(serializer, fields):
    words = re.findall('[A-Z][^A-Z]*', serializer.__name__)
    return f"Partial{''.join(words[:-1])}_{'_'.join(sorted(fields))}"


def get_serializer_with_fields(serializer, allowed_fields: list, name=None):
    """
    Returns a new serializer with the specified fields.
    """

    class NewSerializer(serializer):
        def __init__(self, *args, **kwargs):
            NewSerializer.__name__ = name or partial_serializer_name(serializer, allowed_fields)

            super(NewSerializer, self).__init__(*args, **kwargs)

            if allowed_fields is not None:
                allowed = set(allowed_fields)
                existing = set(self.fields)
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

    return NewSerializer


partial_serializers_by_name: dict[str, Type] = {}


class BaseModelSerializer(serializers.ModelSerializer):
    @classmethod
    def with_fields(cls, fields):
        name = partial_serializer_name(cls, fields)
        if name not in partial_serializers_by_name:
            partial_serializers_by_name[name] = get_serializer_with_fields(
                cls,
                fields,
                name)
        return partial_serializers_by_name[name]


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
