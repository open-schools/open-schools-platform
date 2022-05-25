import inspect
import sys

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    PermissionDenied,
    ObjectDoesNotExist
)
from django.http import Http404

from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError as RestValidationError, APIException

from open_schools_platform.user_management.users.models import User
from open_schools_platform.core.exceptions import ApplicationError


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


class TriggerNotFounded(APIException):
    def __init__(self, status=404, detail="Not found"):
        self.status_code = status
        self.detail = detail


class TriggerNotAcceptable(APIException):
    def __init__(self, status=406, detail="Not acceptable"):
        self.status_code = status
        self.detail = detail


class TriggerAuthFailed(APIException):
    def __init__(self, status=401, detail="Authentication failed"):
        self.status_code = status
        self.detail = detail


class TriggerTimeoutError(APIException):
    def __init__(self, status=500, detail="Timeout error"):
        self.status_code = status
        self.detail = detail


class TriggerValidationError(APIException):
    def __init__(self, status=400, detail="Validation error"):
        self.status_code = status
        self.detail = detail


def trigger_errors(exception_handler):
    result = {}

    for name, member in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(member) and name.startswith("trigger") and name != "trigger_errors":
            try:
                member()
            except Exception as exc:
                response = exception_handler(exc, {})

                if response is None:
                    result[name] = "500 SERVER ERROR"
                    continue

                result[name] = response.data
        if inspect.isclass(member) and name.startswith("Trigger"):
            try:
                raise member
            except Exception as exc:
                response = exception_handler(exc, {})

                if response is None:
                    result[name] = "500 SERVER ERROR"
                    continue

                result[name] = response.data

    return result
