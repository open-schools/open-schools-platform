import inspect
import sys

import rest_framework
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    PermissionDenied,
    ObjectDoesNotExist
)
from django.http import Http404

from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError as RestValidationError, APIException, ErrorDetail

from open_schools_platform.errors.exceptions import ApplicationError
from open_schools_platform.user_management.users.models import User


class NestedSerializer(serializers.Serializer):
    bar = serializers.CharField()


class PlainSerializer(serializers.Serializer):
    foo = serializers.CharField()
    email = serializers.EmailField(min_length=200)

    nested = NestedSerializer()


def trigger_django_validation():
    raise DjangoValidationError("Some error message")


def trigger_django_permission_denied():
    raise PermissionDenied()


def trigger_django_object_does_not_exist():
    raise ObjectDoesNotExist()


def trigger_django_404():
    raise Http404()


def trigger_model_clean():
    user = User()
    user.full_clean()


def trigger_rest_validation_plain():
    raise RestValidationError("An Error occurred")


def trigger_rest_validation_detail():
    raise RestValidationError(detail={"error": "Some error message"})


def trigger_serialization_validation():
    serializer = PlainSerializer(data={
        "email": "foo",
        "nested": {}
    })
    serializer.is_valid(raise_exception=True)


def trigger_rest_throttled():
    raise exceptions.Throttled()


def trigger_rest_unsupported_media_type():
    raise exceptions.UnsupportedMediaType(media_type="a/b")


def trigger_rest_not_acceptable():
    raise exceptions.NotAcceptable()


def trigger_rest_method_not_allowed():
    raise exceptions.MethodNotAllowed(method="POST")


def trigger_rest_not_found():
    raise exceptions.NotFound()


def trigger_rest_permission_denied():
    raise exceptions.PermissionDenied()


def trigger_rest_not_authenticated():
    raise exceptions.NotAuthenticated()


def trigger_rest_authentication_failed():
    raise exceptions.AuthenticationFailed()


def trigger_rest_parse_error():
    raise exceptions.ParseError()


def trigger_application_error():
    raise ApplicationError(message="Something is not correct", extra={"type": "RANDOM"})


def trigger_errors(exception_handler):
    result = {}

    members = inspect.getmembers(sys.modules[__name__],
                                 lambda obj: (inspect.isclass(obj) or inspect.isfunction(
                                     obj)) and obj.__module__ == __name__)
    members.extend([mem for mem in inspect.getmembers(rest_framework.exceptions, inspect.isclass) if
                    mem[1].__module__ == rest_framework.exceptions.__name__ and mem[1] not in (
                        ErrorDetail, APIException)])

    for name, member in members:
        if inspect.isfunction(member) and name.startswith("trigger") and name != "trigger_errors":
            try:
                member()
            except Exception as exc:
                response = exception_handler(exc, {})

                if response is None:
                    result[name] = "500 SERVER ERROR"
                    continue

                response.data['status_code'] = response.status_code
                result[name] = response.data
        if inspect.isclass(member) and not name.endswith("Serializer"):
            try:
                raise member
            except Exception as exc:
                response = exception_handler(exc, {})

                if response is None:
                    result[name] = "500 SERVER ERROR"
                    continue

                response.data['status_code'] = response.status_code
                result[name] = response.data

    return result
