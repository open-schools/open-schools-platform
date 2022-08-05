from django.contrib.contenttypes.models import ContentType
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.organization_management.employees.filters import EmployeeFilter
from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.paginators import EmployeeApiListPagination
from open_schools_platform.organization_management.employees.selectors import get_employees, get_employee_profile
from open_schools_platform.organization_management.employees.serializers import EmployeeListSerializer
from open_schools_platform.organization_management.organizations.selectors import get_organization

from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.query_management.queries.serializers import EmployeeProfileQuerySerializer


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
        filters = request.GET.dict()
        if "organization" not in filters.keys():
            raise NotAcceptable("Your request should contain organization field.")
        get_organization(filters={"id": filters["organization"]}, user=request.user)
        response = get_paginated_response(
            pagination_class=EmployeeApiListPagination,
            serializer_class=EmployeeListSerializer,
            queryset=get_employees(filters=request.GET.dict()),
            request=request,
            view=self
        )
        return response


class EmployeeQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Get all queries for the provided employee profile",
        responses={200: swagger_dict_response({"results": EmployeeProfileQuerySerializer(many=True)})}
    )
    def get(self, request):
        employee_profile = get_employee_profile(filters={'id': str(request.user.employee_profile.id)},
                                                user=request.user)
        if employee_profile is None:
            raise NotFound('There is no such student profile')
        queries = get_queries(
            filters={'recipient_id': str(employee_profile.id),
                     'sender_ct': ContentType.objects.get(model="organization")})

        if not queries:
            raise NotFound('There are no queries with such content type')

        return Response({"results": EmployeeProfileQuerySerializer(queries, many=True).data}, status=200)
