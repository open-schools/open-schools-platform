from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class InvalidArgumentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST  # status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("Some of input data are invalid.")
    default_code = 'invalid_input'


class QueryCorrupted(APIException):
    status_code = status.HTTP_400_BAD_REQUEST  # status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = _('Query is corrupted')
    default_code = 'query_corrupted'


class WrongStatusChange(APIException):
    status_code = status.HTTP_400_BAD_REQUEST  # status.HTTP_406_NOT_ACCEPTABLE
    default_detail = _('Failed to set this status in the current context.')
    default_code = 'wrong_status'
