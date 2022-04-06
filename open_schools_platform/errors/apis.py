from rest_framework.views import APIView
from rest_framework.response import Response

from open_schools_platform.api.exception_handlers import (
    drf_default_with_modifications_exception_handler,
    hacksoft_proposed_exception_handler
)

from open_schools_platform.errors.services import trigger_errors
from open_schools_platform.user_management.users.services import create_user


class TriggerErrorApi(APIView):
    def get(self, request):
        data = {
            "drf_default_with_modifications": trigger_errors(drf_default_with_modifications_exception_handler),
            "hacksoft_proposed": trigger_errors(hacksoft_proposed_exception_handler)
        }

        return Response(data)


class TriggerValidateUniqueErrorApi(APIView):
    def get(self, request):
        # Due to the fiddling with transactions, this example a different API
        create_user(
            phone="+79112112943",
            name="Ivan",
            password="qwe",
        )
        create_user(
            phone="+79112112943",
            name="Ivan",
            password="qwe",
        )

        return Response()


class TriggerUnhandledExceptionApi(APIView):
    def get(self, request):
        raise Exception("Oops")

        return Response()
