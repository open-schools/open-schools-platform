from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response

from open_schools_platform.api.exception_handlers import (
    drf_default_with_modifications_exception_handler,
    proposed_exception_handler
)
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.serializers import Error400Serializer, Error401Serializer
from open_schools_platform.common.views import convert_dict_to_serializer

from open_schools_platform.errors.services import trigger_errors


class TriggerApiException(APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ERRORS],
        responses={400: convert_dict_to_serializer({'error': Error400Serializer()}),
                   401: convert_dict_to_serializer({'error': Error401Serializer()})}
    )
    def get(self, request):
        data = {
            "drf_default_with_modifications": trigger_errors(drf_default_with_modifications_exception_handler),
            "proposed": trigger_errors(proposed_exception_handler)
        }

        return Response(data)
