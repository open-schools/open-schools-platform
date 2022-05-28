from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.employees.serializers import EmployeeSerializer, \
    CreateEmployeeSerializer
from open_schools_platform.organization_management.employees.services import add_employee_to_organization


class EmployeeApi(ApiAuthMixin, CreateAPIView):
    serializer_class = CreateEmployeeSerializer

    @swagger_auto_schema(
        operation_description="Create employee with attached organization and user",
        request_body=CreateEmployeeSerializer,
        responses={201: EmployeeSerializer},
        tags=[SwaggerTags.organization_management_employees],
    )
    def post(self, request, *args, **kwargs):
        employee_serializer = self.serializer_class(data=request.data)
        employee_serializer.is_valid(raise_exception=True)

        employee = add_employee_to_organization(request.user, **employee_serializer.validated_data)

        return Response({"employee": EmployeeSerializer(employee).data},
                        status=201)
