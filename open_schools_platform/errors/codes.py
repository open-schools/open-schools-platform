from rest_framework.exceptions import ValidationError, ParseError, NotAuthenticated, AuthenticationFailed

from open_schools_platform.errors.exceptions import InvalidArgument, QueryCorrupted, WrongStatusChange, \
    EmailServiceUnavailable, AlreadyExists, MapServiceUnavailable, TicketIsClosed

error_codes = {
    400: [ValidationError, ParseError, InvalidArgument, QueryCorrupted, WrongStatusChange,
          EmailServiceUnavailable, AlreadyExists, MapServiceUnavailable, TicketIsClosed],
    401: [AuthenticationFailed, NotAuthenticated]
}
