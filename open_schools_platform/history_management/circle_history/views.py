from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.history_management.circle_history.serializers import CircleHistorySerializer
from open_schools_platform.organization_management.circles.selectors import get_circle
from open_schools_platform.common.views import swagger_dict_response


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get circle history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': CircleHistorySerializer(many=True)}),
                   404: "There is no such circle"},
    )
    def get(self, request, pk):
        organization = get_circle(filters={"id": pk},
                                  empty_exception=True,
                                  empty_message="There is no such circle")
        return Response({"results": CircleHistorySerializer(organization).data}, status=200)
