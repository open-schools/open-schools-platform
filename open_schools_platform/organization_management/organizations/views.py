from django_filters import UUIDFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotAcceptable
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.organization_management.circles.selectors import get_circle
from open_schools_platform.organization_management.employees.serializers import EmployeeSerializer, \
    OrganizationEmployeeInviteUpdateSerializer, OrganizationEmployeeInviteSerializer
from open_schools_platform.organization_management.employees.services import create_employee, \
    get_employee_profile_or_create_new_user, update_invite_employee_body
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.paginators import OrganizationApiListPagination
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user, \
    get_organization
from open_schools_platform.organization_management.organizations.serializers import CreateOrganizationSerializer, \
    OrganizationSerializer
from open_schools_platform.organization_management.organizations.services import create_organization, \
    organization_circle_query_filter
from open_schools_platform.common.services import get_object_by_id_in_field_with_checks
from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer, \
    EmployeeProfileQuerySerializer, StudentProfileQuerySerializer
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.filters import StudentFilter
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.student_management.students.selectors import get_students
from open_schools_platform.student_management.students.serializers import StudentSerializer


class OrganizationCreateApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create organization and related to it employee for this user.",
        request_body=CreateOrganizationSerializer,
        responses={201: swagger_dict_response({"creator_employee": EmployeeSerializer()})},
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS]
    )
    def post(self, request, *args, **kwargs):
        org_serializer = CreateOrganizationSerializer(data=request.data)
        org_serializer.is_valid(raise_exception=True)

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
        request_body=OrganizationEmployeeInviteSerializer,
        responses={201: swagger_dict_response({"query": QueryStatusSerializer()})},
        operation_description="Creates invite employee query.",
    )
    def post(self, request, pk) -> Response:
        invite_serializer = OrganizationEmployeeInviteSerializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)

        phone = invite_serializer.validated_data["phone"]
        email = invite_serializer.validated_data["email"]
        name = invite_serializer.validated_data["body"]["name"]
        organization = get_organization(filters={"id": pk})

        employee_profile = get_employee_profile_or_create_new_user(phone=phone.__str__(), email=str(email),
                                                                   organization_name=organization.name, name=name)

        employee = create_employee(**invite_serializer.validated_data["body"])

        query = create_query(sender_model_name="organization", sender_id=pk,
                             recipient_model_name="employeeprofile", recipient_id=employee_profile.id,
                             body_model_name="employee", body_id=employee.id)

        return Response({"query": QueryStatusSerializer(query).data},
                        status=201)


class InviteEmployeeUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        request_body=OrganizationEmployeeInviteUpdateSerializer,
        responses={200: swagger_dict_response({"query": EmployeeProfileQuerySerializer()}),
                   404: "There is no such query",
                   406: "Cant update query because it's status is not SENT"},
        operation_description="Update body of invite employee query",
    )
    def put(self, request):
        query_update_serializer = OrganizationEmployeeInviteUpdateSerializer(data=request.data)
        query_update_serializer.is_valid(raise_exception=True)
        query = get_query_with_checks(
            pk=str(query_update_serializer.validated_data["query"]),
            user=request.user,
            update_query_check=True
        )
        update_invite_employee_body(
            query=query,
            data=query_update_serializer["body"]
        )
        return Response({"query": EmployeeProfileQuerySerializer(query).data}, status=200)


class OrganizationEmployeeQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: swagger_dict_response({"results": EmployeeProfileQuerySerializer(many=True)})},
        operation_description="Get all queries for organization of current user",
    )
    def get(self, request, pk):
        organization = get_organization(
            filters={'id': str(pk)},
            user=request.user,
            empty_exception=True,
            empty_message="There is no such organization"
        )
        queries = get_queries(
            filters={'sender_id': organization.id},
            empty_exception=True,
            empty_message="There are no queries with such sender"
        )
        return Response({"results": EmployeeProfileQuerySerializer(queries, many=True).data}, status=200)


class OrganizationCircleQueriesListApi(ApiAuthMixin, ListAPIView):
    class FilterProperties:
        query_fields = QueryFilter.get_swagger_filters(prefix="query")
        student_fields = StudentFilter.get_swagger_filters(prefix="student", include=["name", "student_profile__phone"])
        additional_fields = {"organization": UUIDFilter(lookup_expr=["exact"]),
                             "circle": UUIDFilter(lookup_expr=["exact"])}

    queryset = Query.objects.all()
    swagger_filter_fields = \
        FilterProperties.query_fields | \
        FilterProperties.student_fields | \
        FilterProperties.additional_fields

    @swagger_auto_schema(
        operation_description="Get all queries for provided circle or organization.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: swagger_dict_response({"results": StudentProfileQuerySerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"organization": get_organization, "circle": get_circle}
        )
        if not organization and not circle:
            raise NotAcceptable("You should define organization or circle")

        queries = organization_circle_query_filter(self, filters, organization, circle)

        return Response({"results": StudentProfileQuerySerializer(queries, many=True).data}, status=200)


class OrganizationStudentsListApi(ApiAuthMixin, ListAPIView):
    class FilterProperties:
        student_fields = StudentFilter.get_swagger_filters()

    queryset = Student.objects.all()
    swagger_filter_fields = FilterProperties.student_fields

    @swagger_auto_schema(
        operation_description="Get students in this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: swagger_dict_response({"results": StudentSerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"circle__organization": get_organization, "circle": get_circle}
        )
        if not organization and not circle:
            raise NotAcceptable("You should define organization or circle")

        students = get_students(filters=filters)

        return Response({"results": StudentSerializer(students, many=True).data}, status=200)


class OrganizationDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Delete organization.",
        responses={200: "Success deletion", 404: "There is no such organization"}
    )
    def delete(self, request, pk):
        organization = get_organization(filters={'id': pk}, empty_exception=True)
        organization.delete()
        return Response("Success deletion", status=200)
