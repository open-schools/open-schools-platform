from django_filters import UUIDFilter
from drf_yasg import openapi
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING, FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin, XLSXMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.circles.paginators import ApiCircleListPagination
from open_schools_platform.organization_management.circles.selectors import get_circle
from open_schools_platform.organization_management.employees.serializers import EmployeeSerializer, \
    OrganizationEmployeeInviteUpdateSerializer, OrganizationEmployeeInviteSerializer
from open_schools_platform.organization_management.employees.services import create_employee, \
    get_employee_profile_or_create_new_user, update_invite_employee_body
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.paginators import OrganizationApiListPagination
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user, \
    get_organization, get_organization_circle_queries
from open_schools_platform.organization_management.organizations.serializers import CreateOrganizationSerializer, \
    OrganizationSerializer, AnalyticsSerializer
from open_schools_platform.organization_management.organizations.services import create_organization, \
    organization_circle_query_filter, filter_organization_circle_queries_by_dates
from open_schools_platform.common.services import get_object_by_id_in_field_with_checks
from open_schools_platform.organization_management.teachers.selectors import get_teacher
from open_schools_platform.organization_management.teachers.serializers import TeacherSerializer
from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer, \
    EmployeeProfileQuerySerializer, StudentProfileQuerySerializer
from open_schools_platform.query_management.queries.services import create_query, count_queries_by_statuses
from open_schools_platform.student_management.students.filters import StudentFilter
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.student_management.students.selectors import get_students, get_student, get_student_profile
from open_schools_platform.student_management.students.serializers import StudentSerializer, StudentGetSerializer
from open_schools_platform.student_management.students.services import export_students


class OrganizationCreateApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create organization and related to it employee for this user.",
        request_body=CreateOrganizationSerializer,
        responses={201: convert_dict_to_serializer({"creator_employee": EmployeeSerializer()})},
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
        responses={201: convert_dict_to_serializer({"query": QueryStatusSerializer()})},
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
        responses={200: convert_dict_to_serializer({"query": EmployeeProfileQuerySerializer()}),
                   400: "Cant update query because it's status is not SENT",
                   404: "No such query"},
        operation_description="Update body of invite employee query",
    )
    def patch(self, request):
        query_update_serializer = OrganizationEmployeeInviteUpdateSerializer(data=request.data)
        query_update_serializer.is_valid(raise_exception=True)
        query = get_query_with_checks(
            pk=str(query_update_serializer.validated_data["query"]),
            user=request.user,
            update_query_check=True
        )
        update_invite_employee_body(
            query=query,
            data=query_update_serializer.validated_data["body"]
        )
        return Response({"query": EmployeeProfileQuerySerializer(query).data}, status=200)


class OrganizationEmployeeQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": EmployeeProfileQuerySerializer(many=True)})},
        operation_description="Get all queries for organization of current user",
    )
    def get(self, request, pk):
        organization = get_organization(
            filters={'id': str(pk)},
            user=request.user,
            empty_exception=True,
        )
        queries = get_queries(filters={'sender_id': str(organization.id)})
        return Response({"results": EmployeeProfileQuerySerializer(queries, many=True).data}, status=200)


class OrganizationCircleQueriesListApi(ApiAuthMixin, ListAPIView):
    class FilterProperties:
        query_fields = QueryFilter.get_swagger_filters(prefix="query")
        student_fields = StudentFilter.get_swagger_filters(prefix="student", include=["name", "student_profile__phone"])
        additional_fields = {"organization": UUIDFilter(lookup_expr=["exact"]),
                             "circle": UUIDFilter(lookup_expr=["exact"])}

    queryset = Query.objects.all()
    visible_filter_fields = \
        FilterProperties.query_fields | \
        FilterProperties.student_fields | \
        FilterProperties.additional_fields

    @swagger_auto_schema(
        operation_description="Get all queries for provided circle or organization.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": StudentProfileQuerySerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"organization": get_organization, "circle": get_circle}
        )
        if not organization and not circle:
            raise ValidationError("You should define organization or circle")

        queries = organization_circle_query_filter(self, filters, organization, circle)

        return Response({"results": StudentProfileQuerySerializer(queries, many=True).data}, status=200)


class OrganizationStudentsListApi(ApiAuthMixin, ListAPIView):
    class FilterProperties:
        student_fields = StudentFilter.get_swagger_filters()

    queryset = Student.objects.all()
    visible_filter_fields = FilterProperties.student_fields

    @swagger_auto_schema(
        operation_description="Get students in this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": StudentSerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"circle__organization": get_organization, "circle": get_circle}
        )
        if not organization and not circle:
            raise ValidationError("You should define organization or circle")

        students = get_students(filters=filters)

        return Response({"results": StudentSerializer(students, many=True).data}, status=200)


class OrganizationDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Delete organization.",
        responses={204: "Successfully deleted", 404: "No such organization"}
    )
    def delete(self, request, pk):
        organization = get_organization(filters={'id': pk}, empty_exception=True, user=request.user)
        organization.delete()
        return Response(status=204)


class GetStudentApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get student with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"student": StudentGetSerializer()}), 404: "No such student"}
    )
    def get(self, request, pk):
        student = get_student(
            filters={"id": str(pk)}, user=request.user,
            empty_exception=True,
        )
        return Response({"student": StudentGetSerializer(student).data}, status=200)


class OrganizationStudentProfilesExportApi(ApiAuthMixin, XLSXMixin, APIView):
    filename = 'organization_students.xlsx'

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Export students from this organization",
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))}
    )
    def get(self, request, pk):
        get_organization(filters={'id': str(pk)}, user=request.user, empty_exception=True)
        students = get_students(filters={'circle__organization': str(pk)})
        file = export_students(students, export_format='xlsx')
        return Response(file, status=200)


class GetAnalytics(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Get analytics for this organization",
        manual_parameters=[
            Parameter('date_from', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
            Parameter('date_to', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
        ],
        responses={200: convert_dict_to_serializer({"analytics": AnalyticsSerializer()}),
                   404: "There is no such organization"}
    )
    def get(self, request, pk):
        dates = request.GET.dict()
        organization = get_organization(filters={"id": str(pk)}, empty_exception=True, user=request.user)
        queries = get_organization_circle_queries(organization)
        if all(arg in dates for arg in ("date_from", "date_to")):
            queries = filter_organization_circle_queries_by_dates(queries, dates["date_from"], dates["date_to"])
        return Response({"analytics": AnalyticsSerializer(count_queries_by_statuses(queries)).data}, status=200)


class OrganizationStudentProfileQueriesApi(ApiAuthMixin, ListAPIView):
    pagination_class = ApiCircleListPagination
    queryset = Query.objects.all()
    serializer_class = StudentProfileQuerySerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Returns queries to student circles from the selected organization",
    )
    def get(self, request, organization, student_profile, *args, **kwargs):
        get_student_profile(
            filters={"id": str(student_profile)},
            empty_exception=True
        )
        organization = get_organization(
            filters={"id": str(organization)},
            user=request.user,
            empty_exception=True
        )
        queries = get_queries(
            filters={"sender_id": str(student_profile),
                     "recipient_ids": form_ids_string_from_queryset(organization.circles.values())}
        )

        response = get_paginated_response(
            pagination_class=ApiCircleListPagination,
            serializer_class=StudentProfileQuerySerializer,
            queryset=queries,
            request=request,
            view=self
        )
        return response


class OrganizationTeachersListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all teachers for this organization",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": TeacherSerializer(many=True)})}
    )
    def get(self, request, pk):
        organization = get_organization(filters={"id": str(pk)}, empty_exception=True, user=request.user)
        return Response({"results": TeacherSerializer(organization.teachers, many=True).data}, status=200)


class GetTeacherApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get teacher with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"teacher": TeacherSerializer()})}
    )
    def get(self, request, pk):
        teacher = get_teacher(filters={"id": str(pk)}, empty_exception=True, user=request.user)
        return Response({"teacher": TeacherSerializer(teacher).data}, status=200)
