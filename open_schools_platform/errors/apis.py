from rest_framework.views import APIView
from rest_framework.response import Response

from open_schools_platform.api.exception_handlers import (
    drf_default_with_modifications_exception_handler,
    hacksoft_proposed_exception_handler
)

from open_schools_platform.errors.services import trigger_errors


class TriggerApiException(APIView):
    def get(self, request):
        data = {
            "drf_default_with_modifications": trigger_errors(drf_default_with_modifications_exception_handler),
            "hacksoft_proposed": trigger_errors(hacksoft_proposed_exception_handler)
        }

        return Response(data)
