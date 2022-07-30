from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import get_dict_excluding_fields
from open_schools_platform.organization_management.employees.serializers import EmployeeSerializer
from open_schools_platform.organization_management.employees.services import create_employee, \
    get_employee_profile_or_create_new_user, update_invite_employee_body
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.paginators import OrganizationApiListPagination
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user, \
    get_organization
from open_schools_platform.organization_management.organizations.serializers import CreateOrganizationSerializer, \
    OrganizationSerializer, OrganizationInviteSerializer, OrganizationInviteUpdateSerializer
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer, \
    OrganizationQuerySerializer
from open_schools_platform.query_management.queries.services import create_query


class OrganizationCreateApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create organization and related to it employee for this user.",
        request_body=CreateOrganizationSerializer,
        responses={201: EmployeeSerializer},
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS]
    )
    def post(self, request, *args, **kwargs):
        org_serializer = CreateOrganizationSerializer(data=request.data)
        org_serializer.is_valid()

        org = create_organization(**org_serializer.validated_data)

        employee = create_employee(name=request.user.name,
                                   user=request.user,
                                   organization=org,
                                   position="Creator")

        return Response({"creator_employee": EmployeeSerializer(employee).data},
                        status=201)


class OrganizationListApi(ApiAuthMixin, ListAPIView):
    queryset = Organization.objects.all()
    pagination_class = OrganizationApiListPagination
    serializer_class = OrganizationSerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Return paginated list of organizations.",
    )
    def get(self, request, *args, **kwargs):
        response = get_paginated_response(
            pagination_class=OrganizationApiListPagination,
            serializer_class=OrganizationSerializer,
            queryset=get_organizations_by_user(request.user),
            request=request,
            view=self
        )
        return response


class InviteEmployeeApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        request_body=OrganizationInviteSerializer,
        responses={201: QueryStatusSerializer},
        operation_description="Return paginated list of organizations.",
    )
    def post(self, request, pk) -> Response:
        invite_serializer = OrganizationInviteSerializer(data=request.data)
        invite_serializer.is_valid()

        phone = invite_serializer.validated_data["phone"]

        employee_profile = get_employee_profile_or_create_new_user(phone=phone.__str__())

        employee = create_employee(**get_dict_excluding_fields(dictionary=invite_serializer.validated_data,
                                                               fields=['phone']))

        query = create_query(sender_model_name="organization", sender_id=pk,
                             recipient_model_name="employeeprofile", recipient_id=employee_profile.id,
                             body_model_name="employee", body_id=employee.id)

        return Response({"query": QueryStatusSerializer(query).data},
                        status=201)


class InviteEmployeeUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        request_body=OrganizationInviteUpdateSerializer,
        responses={200: OrganizationQuerySerializer, 404: "There is no such query",
                   406: "Cant update query because it's status is not SENT"},
        operation_description="Update body of invite employee query",
    )
    def put(self, request):
        query_update_serializer = OrganizationInviteUpdateSerializer(data=request.data)
        query_update_serializer.is_valid(raise_exception=True)
        query = get_query_with_checks(
            pk=str(query_update_serializer.validated_data["query"]),
            user=request.user,
            update_query_check=True
        )
        update_invite_employee_body(
            query=query,
            data=get_dict_excluding_fields(query_update_serializer.validated_data, ["query"])
        )
        return Response({"query": OrganizationQuerySerializer(query).data}, status=200)


class OrganizationQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Get all queries for organization of current user",
    )
    def get(self, request, pk):
        organization = get_organization(filters={'id': str(pk)}, user=request.user)
        if not organization:
            raise NotFound('There is no such organization')
        queries = get_queries(filters={'sender_id': organization.id})
        if not queries:
            raise NotFound('There are no queries with such sender')
        return Response({"results": OrganizationQuerySerializer(queries, many=True).data}, status=200)
