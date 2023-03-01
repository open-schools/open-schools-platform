from rest_framework.exceptions import ValidationError, ParseError, NotAuthenticated, AuthenticationFailed

from open_schools_platform.errors.exceptions import InvalidArgumentException, QueryCorrupted, WrongStatusChange, \
    EmailServiceUnavailable, AlreadyExists

error_codes = {
    400: [ValidationError, ParseError, InvalidArgumentException, QueryCorrupted, WrongStatusChange,
          EmailServiceUnavailable, AlreadyExists],
    401: [AuthenticationFailed, NotAuthenticated]
}
