from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class InvalidArgument(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Some of input data are invalid.")
    default_code = 'invalid_input'


class QueryCorrupted(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Query is corrupted')
    default_code = 'query_corrupted'


class WrongStatusChange(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Failed to set this status in the current context.')
    default_code = 'wrong_status_change'


class TicketIsClosed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Failed to perform this action because ticket is closed.')
    default_code = 'ticket_is_closed'


class EmailServiceUnavailable(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Email service is currently unavailable.')
    default_code = 'email_service_unavailable'


class SmsServiceUnavailable(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('SMS service is currently unavailable.')
    default_code = 'sms_service_unavailable'


class AlreadyExists(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("This object already exists")
    default_code = 'already_exists'


class MapServiceUnavailable(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Server cannot handle address')
    default_code = 'map_service_unavailable'


class ExcelValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Excel row validation error')
    default_code = 'excel_row_error'


class WrongFileType(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Wrong file type')
    default_code = 'wrong_file_type'


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}
