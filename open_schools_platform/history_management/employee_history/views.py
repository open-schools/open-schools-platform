from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.history_management.employee_history.serializers import EmployeeHistorySerializer
from open_schools_platform.organization_management.employees.selectors import get_employee
from open_schools_platform.common.views import swagger_dict_response


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get employee history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': EmployeeHistorySerializer(many=True)}),
                   404: "There is no such employee"},
    )
    def get(self, request, pk):
        employee = get_employee(filters={"id": pk},
                                empty_exception=True,
                                empty_message="There is no such employee")
        return Response({"results": EmployeeHistorySerializer(employee).data}, status=200)
