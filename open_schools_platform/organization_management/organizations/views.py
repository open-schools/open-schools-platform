from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.employee_management.employees.serializers import CreateEmployeeSerializer
from open_schools_platform.employee_management.employees.services import create_employee
from open_schools_platform.organization_management.organizations.serializers import CreateOrganizationSerializer
from open_schools_platform.organization_management.organizations.services import create_organization


class OrganizationApi(ApiAuthMixin, CreateAPIView):
    serializer_class = CreateOrganizationSerializer

    @swagger_auto_schema(
        operation_description="Create organization and related to it employee for this user",
        request_body=CreateOrganizationSerializer,
        responses={200: "Created"}
    )
    def post(self, request, *args, **kwargs):
        org_serializer = self.serializer_class(data=request.data)
        org_serializer.is_valid()

        org = create_organization(**org_serializer.validated_data)

        employee = create_employee(name=request.user.name,
                                   user=request.user,
                                   organization=org,
                                   position="Creator")

        return Response({"organization": self.serializer_class(org).data,
                         "creator_employee": CreateEmployeeSerializer(employee).data},
                        status=201)
