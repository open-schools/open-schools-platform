import typing

from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.services import get_object_by_id_in_field_with_checks
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.employees.filters import EmployeeFilter
from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.paginators import EmployeeApiListPagination
from open_schools_platform.organization_management.employees.selectors import get_employees, get_employee_profile, \
    get_employee
from open_schools_platform.organization_management.employees.serializers import GetListEmployeeSerializer, \
    GetEmployeeSerializer, UpdateEmployeeSerializer
from open_schools_platform.organization_management.employees.services import update_employee
from open_schools_platform.organization_management.organizations.selectors import get_organization

from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.query_management.queries.serializers import GetOrganizationInviteEmployeeSerializer


class EmployeeListApi(ApiAuthMixin, ListAPIView):
    queryset = Employee.objects.all()
    pagination_class = EmployeeApiListPagination
    serializer_class = GetListEmployeeSerializer
    filterset_class = EmployeeFilter

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Return paginated list of employees.",
    )
    def get(self, request, *args, **kwargs):
        filters = request.GET.dict()
        organization, employee_profile = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"organization": get_organization, "employee_profile": get_employee_profile}
        )
        if not organization and not employee_profile:
            raise ValidationError({'non_field_errors': 'You should define organization or employee_profile',
                                   'organization': ErrorDetail('', code='required'),
                                   'employee_profile': ErrorDetail('', code='required')})

        @typing.no_type_check
        def convert(x: Employee):
            x.phone = x.employee_profile.user.phone
            x.organization__name = x.organization.name
            return x

        response = get_paginated_response(
            pagination_class=EmployeeApiListPagination,
            serializer_class=GetListEmployeeSerializer,
            queryset=list(map(convert, get_employees(filters=request.GET.dict()))),
            request=request,
            view=self
        )
        return response


class EmployeeQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Get all queries for the provided employee profile",
        responses={200: convert_dict_to_serializer({"results": GetOrganizationInviteEmployeeSerializer(many=True)})}
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

        return Response({"results": GetOrganizationInviteEmployeeSerializer(queries, many=True).data}, status=200)


class EmployeeUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        request_body=UpdateEmployeeSerializer,
        operation_description="Update data of provided employee.",
        responses={200: convert_dict_to_serializer({"employee": GetEmployeeSerializer()}), 404: "No such employee"}
    )
    def patch(self, request, employee_id):
        employee_update_serializer = UpdateEmployeeSerializer(data=request.data)
        employee_update_serializer.is_valid()
        employee = get_employee(
            filters={"id": str(employee_id)},
            empty_exception=True,
        )
        get_employee_profile(filters={"id": str(employee.employee_profile.id)}, user=request.user)
        update_employee(employee=employee, data=employee_update_serializer.validated_data)
        return Response({"employee": GetEmployeeSerializer(employee).data}, status=200)


class EmployeeDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_EMPLOYEES],
        operation_description="Delete employee.",
        responses={204: "Successfully deleted", 404: "No such employee"}
    )
    def delete(self, request, employee_id):
        employee = get_employee(filters={'id': employee_id}, empty_exception=True, user=request.user)
        employee.delete()
        return Response(status=204)
