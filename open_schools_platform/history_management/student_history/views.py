from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.history_management.student_history.serializers import StudentHistorySerializer
from open_schools_platform.student_management.students.selectors import get_student


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get student history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': StudentHistorySerializer(many=True)}),
                   404: "There is no such student"},
    )
    def get(self, request, pk):
        student = get_student(filters={"id": pk},
                              empty_exception=True,
                              empty_message="There is no such student")
        return Response({"results": StudentHistorySerializer(student).data}, status=200)
