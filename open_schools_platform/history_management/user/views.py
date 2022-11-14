from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.history_management.user.serializers import UserHistorySerializer
from open_schools_platform.user_management.users.selectors import get_user


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get User history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: "Correct"},
    )
    def get(self, request, pk):
        user = get_user(filters={"id": pk})
        return Response({"user": UserHistorySerializer(user).data}, status=200)
