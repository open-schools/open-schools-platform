from typing import Optional, Dict, Any

from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404

from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from rest_framework.serializers import as_serializer_error
from rest_framework.response import Response

from open_schools_platform.errors.exceptions import ApplicationError
from open_schools_platform.errors.codes import error_codes


def drf_default_with_modifications_exception_handler(exc, ctx):
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))
    elif isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response
    # ErrorDetail
    response.data = {'error': create_error(exc).data}
    return response


def create_error(exception):
    violations = []
    violations_dict: Optional[Dict[str, str]] = {}

    if isinstance(exception.detail, dict):
        if 'non_field_errors' in exception.detail:
            violations = process_detail(exception.detail['non_field_errors'], lambda d: getattr(d, 'code', d))
        violations_dict = process_detail(exception.detail, lambda d: getattr(d, 'code', d))
        violations_dict = {key: violations_dict[key] for key in violations_dict if key != 'non_field_errors'}
    else:
        violations = process_detail(exception.detail, lambda d: getattr(d, 'code', d))

    code = None
    if exception.status_code in error_codes and type(exception) in error_codes[exception.status_code]:
        code = type(exception).__name__
    violations_dict = None if len(violations_dict) == 0 else violations_dict
    if not isinstance(violations, list):
        violations = [violations]
    violations = None if len(violations) == 0 else violations

    message = None
    if isinstance(exception.detail, dict):
        message = '. '.join(
            map(lambda item: f"'{item[0]}': {', '.join(item[1])}", process_detail(exception.detail).items()))
    else:
        message = '. '.join(process_detail(exception.detail))
    from open_schools_platform.common.serializers import ErrorSerializer
    return ErrorSerializer(
        {'message': message, 'violation_fields': violations_dict, 'code': code, 'violations': violations})


def process_detail(detail, selector=lambda d: d):
    if isinstance(detail, dict):
        expanded_detail = expand_nested(detail)
        return {key: process_detail(expanded_detail[key], selector) for key in expanded_detail}
    if isinstance(detail, list):
        return list(map(selector, detail))
    return [selector(detail), ]


def expand_nested(dictionary: dict):
    result: Dict[str, Any] = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            temp = expand_nested(value)
            result = dict(result, **dict([(f'{key}.{i}', temp[i]) for i in temp if temp[i] is not None]))
        else:
            result[key] = value
    return result


def proposed_exception_handler(exc, ctx):
    """
    {
        "message": "Error message",
        "extra": {}
    }
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        if isinstance(exc, ApplicationError):
            data = {
                "message": exc.message,
                "extra": exc.extra
            }
            return Response(data, status=400)

        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {
            "detail": response.data
        }

    if isinstance(exc, exceptions.ValidationError):
        response.data["message"] = "Validation error"
        response.data["extra"] = {
            "fields": response.data["detail"]
        }
    else:
        response.data["message"] = response.data["detail"]
        response.data["extra"] = {}

    del response.data["detail"]

    return response
