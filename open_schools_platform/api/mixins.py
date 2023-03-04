from typing import Sequence, Type, TYPE_CHECKING

from importlib import import_module

from django.conf import settings
from django.utils.encoding import escape_uri_path
from rest_framework.response import Response
from django.contrib import auth
from django.http import HttpResponse

from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import SessionAuthentication, BaseAuthentication

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_auth_header(headers):
    value = headers.get('Authorization')

    if not value:
        return None

    items = value.split()
    if len(items) < 2:
        return None

    auth_type, auth_value = items[:2]

    return auth_type, auth_value


class SessionAsHeaderAuthentication(BaseAuthentication):
    """
    In case we are dealing with issues like Safari not supporting SameSite=None,
    And the client passes the session as Authorization header:

    Authorization: Session 7wvz4sxcp3chm9quyw015n6ryre29b3u

    Run the standard Django auth & try obtaining user.
    """

    def authenticate(self, request):
        auth_header = get_auth_header(request.headers)

        if auth_header is None:
            return None

        auth_type, auth_value = auth_header

        if auth_type != 'Session':
            return None

        engine = import_module(settings.SESSION_ENGINE)
        SessionStore = engine.SessionStore
        session_key = auth_value

        request.session = SessionStore(session_key)
        user = auth.get_user(request)

        return user, None


class CsrfExemptedSessionAuthentication(SessionAuthentication):
    """
    DRF SessionAuthentication is enforcing CSRF, which may be problematic.
    That's why we want to make sure we are exempting any kind of CSRF checks for APIs.
    """

    def enforce_csrf(self, request):
        return


if TYPE_CHECKING:
    # This is going to be resolved in the stub library
    # https://github.com/typeddjango/djangorestframework-stubs/
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[Type[BasePermission]]


class ApiAuthMixin:
    authentication_classes: Sequence[Type[BaseAuthentication]] = [
        CsrfExemptedSessionAuthentication,
        SessionAsHeaderAuthentication,
        JSONWebTokenAuthentication
    ]
    permission_classes: PermissionClassesType = (IsAuthenticated,)


class FileMixin(object):
    """
        A mixin that can be used to render a file
    """
    filename = "file"
    content_type = ""

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        if isinstance(response, Response) and isinstance(response.data, bytes):
            file = response.data
            response = HttpResponse(file, content_type=self.content_type, status=200)
            response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(self.filename), )
        return response


class XLSXMixin(FileMixin):
    """
    A mixin that can be used to render a XLSX file
    """
    filename = "file.xlsx"
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class ICalMixin(FileMixin):
    filename = "file.ics"
    content_type = 'application/calendar'
