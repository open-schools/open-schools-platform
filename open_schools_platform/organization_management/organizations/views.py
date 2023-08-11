from drf_yasg import openapi
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING, FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, ErrorDetail
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
from open_schools_platform.organization_management.employees.serializers import GetEmployeeSerializer, \
    UpdateOrganizationInviteEmployeeSerializer, CreateOrganizationInviteEmployeeSerializer
from open_schools_platform.organization_management.employees.services import create_employee, \
    get_employee_profile_or_create_new_user, update_invite_employee_body
from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.paginators import OrganizationApiListPagination
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user, \
    get_organization, get_organization_circle_queries
from open_schools_platform.organization_management.organizations.serializers import CreateOrganizationSerializer, \
    GetAnalyticsSerializer, GetOrganizationSerializer
from open_schools_platform.organization_management.organizations.services import create_organization, \
    get_organization_circle_query_filter, filter_organization_circle_queries_by_dates
from open_schools_platform.common.services import get_object_by_id_in_field_with_checks, ComplexFilter
from open_schools_platform.organization_management.teachers.filters import TeacherFilter
from open_schools_platform.organization_management.teachers.models import Teacher
from open_schools_platform.organization_management.teachers.paginators import ApiTeachersListPagination
from open_schools_platform.organization_management.teachers.selectors import get_teacher, \
    get_teachers_from_orgaization_with_filters
from open_schools_platform.organization_management.teachers.serializers import GetTeacherSerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import GetQueryStatusSerializer, \
    GetOrganizationInviteEmployeeSerializer, GetStudentJoinCircleSerializer
from open_schools_platform.query_management.queries.services import create_query, count_queries_by_statuses
from open_schools_platform.student_management.students.filters import StudentFilter
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.student_management.students.selectors import get_students, get_student, get_student_profile
from open_schools_platform.student_management.students.serializers import GetStudentSerializer
from open_schools_platform.student_management.students.services import export_students


class OrganizationCreateApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create organization and related to it employee for this user.",
        request_body=CreateOrganizationSerializer,
        responses={201: convert_dict_to_serializer({"creator_employee": GetEmployeeSerializer()})},
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

        return Response({"creator_employee": GetEmployeeSerializer(employee).data},
                        status=201)


class OrganizationListApi(ApiAuthMixin, ListAPIView):
    queryset = Organization.objects.all()
    pagination_class = OrganizationApiListPagination
    filterset_class = OrganizationFilter
    serializer_class = GetOrganizationSerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Return paginated list of organizations.",
    )
    def get(self, request, *args, **kwargs):
        response = get_paginated_response(
            pagination_class=OrganizationApiListPagination,
            serializer_class=GetOrganizationSerializer,
            queryset=get_organizations_by_user(request.user, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class InviteEmployeeApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        request_body=CreateOrganizationInviteEmployeeSerializer,
        responses={201: convert_dict_to_serializer({"query": GetQueryStatusSerializer()})},
        operation_description="Creates invite employee query.",
    )
    def post(self, request, organization_id) -> Response:
        invite_serializer = CreateOrganizationInviteEmployeeSerializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)

        phone = invite_serializer.validated_data["phone"]
        email = invite_serializer.validated_data["email"]
        name = invite_serializer.validated_data["body"]["name"]
        organization = get_organization(filters={"id": organization_id})

        employee_profile = get_employee_profile_or_create_new_user(phone=phone.__str__(), email=str(email),
                                                                   organization_name=organization.name, name=name)

        employee = create_employee(**invite_serializer.validated_data["body"])

        query = create_query(sender_model_name="organization", sender_id=organization_id,
                             recipient_model_name="employeeprofile", recipient_id=employee_profile.id,
                             body_model_name="employee", body_id=employee.id)

        return Response({"query": GetQueryStatusSerializer(query).data},
                        status=201)


class InviteEmployeeUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        request_body=UpdateOrganizationInviteEmployeeSerializer,
        responses={200: convert_dict_to_serializer({"query": GetOrganizationInviteEmployeeSerializer()}),
                   400: "Cant update query because it's status is not SENT",
                   404: "No such query"},
        operation_description="Update body of invite employee query",
    )
    def patch(self, request):
        query_update_serializer = UpdateOrganizationInviteEmployeeSerializer(data=request.data)
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
        return Response({"query": GetOrganizationInviteEmployeeSerializer(query).data}, status=200)


class OrganizationEmployeeQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": GetOrganizationInviteEmployeeSerializer(many=True)})},
        operation_description="Get all queries for organization of current user",
    )
    def get(self, request, organization_id):
        organization = get_organization(
            filters={'id': str(organization_id)},
            user=request.user,
            empty_exception=True,
        )
        queries = get_queries(filters={'sender_id': str(organization.id)})
        return Response({"results": GetOrganizationInviteEmployeeSerializer(queries, many=True).data}, status=200)


class OrganizationCircleQueriesListApi(ApiAuthMixin, ListAPIView):
    complex_filter = get_organization_circle_query_filter()
    queryset = Query.objects.all()
    visible_filter_fields = complex_filter.get_dict_filters()

    @swagger_auto_schema(
        operation_description="Get all queries for provided circle or organization.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": GetStudentJoinCircleSerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"circle__organization__id": get_organization, "circle__id": get_circle}
        )
        if not organization and not circle:
            raise ValidationError({'non_field_errors': 'You should define organization or circle',
                                   'circle__organization__id': ErrorDetail('', code='required'),
                                   'circle__id': ErrorDetail('', code='required')})

        queries = self.complex_filter.get_objects(filters)

        response = get_paginated_response(
            pagination_class=ApiCircleListPagination,
            serializer_class=GetStudentJoinCircleSerializer,
            queryset=queries,
            request=request,
            view=self
        )

        return response


class OrganizationStudentsListApi(ApiAuthMixin, ListAPIView):
    complex_filter = ComplexFilter(
        filterset_type=StudentFilter,
        selector=get_students,
        include_list=["name", "id", "circle", "student_profile",
                      "student_profile__phone", "circle__name", "circle__organization", "or_search"]
    )
    queryset = Student.objects.all()
    visible_filter_fields = complex_filter.get_dict_filters()

    @swagger_auto_schema(
        operation_description="Get students in this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"results": GetStudentSerializer(many=True)})}
    )
    def get(self, request):
        filters = request.GET.dict()

        organization, circle = get_object_by_id_in_field_with_checks(
            filters,
            request,
            {"circle__organization": get_organization, "circle": get_circle}
        )
        if not organization and not circle:
            raise ValidationError({'non_field_errors': 'You should define organization or circle',
                                   'organization': ErrorDetail('', code='required'),
                                   'circle': ErrorDetail('', code='required')})

        students = OrganizationStudentsListApi.complex_filter.get_objects(filters=filters)

        return Response({"results": GetStudentSerializer(students, many=True, context={'request': request}).data},
                        status=200)


class OrganizationDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Delete organization.",
        responses={204: "Successfully deleted", 404: "No such organization"}
    )
    def delete(self, request, organization_id):
        organization = get_organization(filters={'id': organization_id}, empty_exception=True, user=request.user)
        organization.delete()
        return Response(status=204)


class GetStudentApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get student with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"student": GetStudentSerializer()}), 404: "No such student"}
    )
    def get(self, request, student_id):
        student = get_student(
            filters={"id": str(student_id)}, user=request.user,
            empty_exception=True,
        )
        return Response({"student": GetStudentSerializer(student, context={'request': request}).data}, status=200)


class OrganizationStudentProfilesExportApi(ApiAuthMixin, XLSXMixin, APIView):
    filename = 'organization_students.xlsx'

    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        operation_description="Export students from this organization",
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))}
    )
    def get(self, request, organization_id):
        get_organization(filters={'id': str(organization_id)}, user=request.user, empty_exception=True)
        students = get_students(filters={'circle__organization': str(organization_id)})
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
        responses={200: convert_dict_to_serializer({"analytics": GetAnalyticsSerializer()}),
                   404: "There is no such organization"}
    )
    def get(self, request, organization_id):
        dates = request.GET.dict()
        organization = get_organization(filters={"id": str(organization_id)}, empty_exception=True, user=request.user)
        queries = get_organization_circle_queries(organization)
        if all(arg in dates for arg in ("date_from", "date_to")):
            queries = filter_organization_circle_queries_by_dates(queries, dates["date_from"], dates["date_to"])
        return Response({"analytics": GetAnalyticsSerializer(count_queries_by_statuses(queries)).data}, status=200)


class OrganizationStudentProfileQueriesApi(ApiAuthMixin, ListAPIView):
    pagination_class = ApiCircleListPagination
    queryset = Query.objects.all()
    serializer_class = GetStudentJoinCircleSerializer

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
            serializer_class=GetStudentJoinCircleSerializer,
            queryset=queries,
            request=request,
            view=self
        )
        return response


class OrganizationTeachersListApi(ApiAuthMixin, ListAPIView):
    queryset = Teacher.objects.all()
    filterset_class = TeacherFilter
    pagination_class = ApiTeachersListPagination
    serializer_class = GetTeacherSerializer

    @swagger_auto_schema(
        operation_description="Get all teachers for this organization",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS]
    )
    def get(self, request, organization_id):
        organization = get_organization(filters={"id": str(organization_id)}, empty_exception=True, user=request.user)
        response = get_paginated_response(
            pagination_class=ApiTeachersListPagination,
            serializer_class=GetTeacherSerializer,
            queryset=get_teachers_from_orgaization_with_filters(organization, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class GetTeacherApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get teacher with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_ORGANIZATIONS],
        responses={200: convert_dict_to_serializer({"teacher": GetTeacherSerializer()})}
    )
    def get(self, request, teacher_id):
        teacher = get_teacher(filters={"id": str(teacher_id)}, empty_exception=True, user=request.user)
        return Response({"teacher": GetTeacherSerializer(teacher).data}, status=200)
