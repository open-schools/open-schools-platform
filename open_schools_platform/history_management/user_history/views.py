from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.history_management.user_history.serializers import UserHistorySerializer
from open_schools_platform.user_management.users.selectors import get_user


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get user history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': UserHistorySerializer(many=True)}),
                   404: "There is no such user"},
    )
    def get(self, request, pk):
        user = get_user(filters={"id": pk},
                        empty_exception=True,
                        empty_message="There is no such user")
        return Response({"results": UserHistorySerializer(user).data}, status=200)
