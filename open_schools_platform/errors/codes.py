from rest_framework.exceptions import ValidationError, ParseError, NotAuthenticated, AuthenticationFailed

from open_schools_platform.errors.exceptions import InvalidArgumentException, QueryCorrupted, WrongStatusChange

error_codes = {
    400: [ValidationError, ParseError, InvalidArgumentException, QueryCorrupted, WrongStatusChange],
    401: [AuthenticationFailed, NotAuthenticated]
}
