from typing import Dict, Optional, Any

from rest_framework.exceptions import ValidationError, ParseError, AuthenticationFailed, NotAuthenticated

from open_schools_platform.api.utils import flatten
from open_schools_platform.errors.exceptions import InvalidArgumentException, QueryCorrupted, WrongStatusChange

error_codes = {
    400: [ValidationError.__name__, ParseError.__name__, InvalidArgumentException.__name__, QueryCorrupted.__name__,
          WrongStatusChange.__name__],
    401: [AuthenticationFailed.__name__, NotAuthenticated.__name__]
}


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
    if exception.status_code in error_codes and type(exception).__name__ in error_codes[exception.status_code]:
        code = type(exception).__name__
    violations_dict = None if len(violations_dict) == 0 else violations_dict
    if not isinstance(violations, list):
        violations = [violations]
    violations = None if len(violations) == 0 else violations

    message = None
    if isinstance(exception.detail, dict):
        message = ';\n'.join(
            map(lambda item: f"'{item[0]}': {','.join(item[1])}", flatten(process_detail(exception.detail).items())))
    else:
        message = '\n'.join(flatten(process_detail(exception.detail)))
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
