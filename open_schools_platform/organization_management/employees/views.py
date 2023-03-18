from django.contrib.contenttypes.models import ContentType
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.employees.filters import EmployeeFilter
from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.paginators import EmployeeApiListPagination
from open_schools_platform.organization_management.employees.selectors import get_employees, get_employee_profile, \
    get_employee
from open_schools_platform.organization_management.employees.serializers import EmployeeListSerializer, \
    EmployeeSerializer, EmployeeUpdateSerializer
from open_schools_platform.organization_management.employees.services import update_employee
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
            raise ValidationError({"organization": "Your request should contain organization field."})
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
        responses={200: convert_dict_to_serializer({"results": EmployeeProfileQuerySerializer(many=True)})}
    )
    def get(self, request):
        employee_profile = get_employee_profile(
            filters={'id': str(request.user.employee_profile.id)},
            user=request.user,
            empty_exception=True,
        )

        queries = get_queries(
            filters={'recipient_id': str(employee_profile.id),
                     'sender_ct': ContentType.objects.get(model="organization")})

        return Response({"results": EmployeeProfileQuerySerializer(queries, many=True).data}, status=200)


class EmployeeUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        request_body=EmployeeUpdateSerializer,
        operation_description="Update data of provided employee.",
        responses={200: convert_dict_to_serializer({"employee": EmployeeSerializer()}), 404: "No such employee"}
    )
    def patch(self, request, pk):
        employee_update_serializer = EmployeeUpdateSerializer(data=request.data)
        employee_update_serializer.is_valid()
        employee = get_employee(
            filters={"id": str(pk)},
            empty_exception=True,
        )
        get_employee_profile(filters={"id": str(employee.employee_profile.id)}, user=request.user)
        update_employee(employee=employee, data=employee_update_serializer.validated_data)
        return Response({"employee": EmployeeSerializer(employee).data}, status=200)


class EmployeeDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Delete employee.",
        responses={204: "Successfully deleted", 404: "No such employee"}
    )
    def delete(self, request, pk):
        employee = get_employee(filters={'id': pk}, empty_exception=True, user=request.user)
        employee.delete()
        return Response(status=204)
