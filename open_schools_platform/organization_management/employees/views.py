from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.employees.filters import EmployeeFilter
from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.paginators import EmployeeApiListPagination
from open_schools_platform.organization_management.employees.selectors import get_employees, get_employee
from open_schools_platform.organization_management.employees.serializers import EmployeeListSerializer


class EmployeeListApi(ApiAuthMixin, ListAPIView):
    queryset = Employee.objects.all()
    pagination_class = EmployeeApiListPagination
    serializer_class = EmployeeListSerializer
    filterset_class = EmployeeFilter

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Return paginated list of employees.",
        manual_parameters=[
            Parameter('organization', IN_QUERY, required=True, type=TYPE_STRING),  # type:ignore
        ],
    )
    def get(self, request, *args, **kwargs):
        # TODO: we should add permission checks here
        if not get_employee(filters={"employee_profile": request.user.employee_profile,
                                     "organization": request.GET.get("organization")}):
            raise PermissionDenied(detail="You are not a member of this organization")

        response = get_paginated_response(
            pagination_class=EmployeeApiListPagination,
            serializer_class=EmployeeListSerializer,
            queryset=get_employees(filters=request.GET.dict()),
            request=request,
            view=self
        )
        return response
