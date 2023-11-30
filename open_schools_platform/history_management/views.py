from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.history_management.filters import HistoryFilter
from open_schools_platform.history_management.paginators import ApiHistoryListPagination
from open_schools_platform.history_management.selectors import get_history
from open_schools_platform.history_management.serializers.query_serializer import GetQueryHistorySerializer
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_query
from open_schools_platform.student_management.students.models import Student, StudentProfile
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.organization_management.employees.selectors import get_employee, get_employee_profile
from open_schools_platform.student_management.students.selectors import get_student, get_student_profile
from open_schools_platform.organization_management.circles.selectors import get_circle
from open_schools_platform.history_management.serializers.user_serializer import GetUserHistorySerializer
from open_schools_platform.history_management.serializers.organization_serializer import \
    GetOrganizationHistorySerializer
from open_schools_platform.history_management.serializers.employee_serializer import GetEmployeeHistorySerializer, \
    GetEmployeeProfileHistorySerializer
from open_schools_platform.history_management.serializers.circle_serializer import GetCircleHistorySerializer
from open_schools_platform.history_management.serializers.student_serializer import GetStudentHistorySerializer, \
    GetStudentProfileHistorySerializer
from open_schools_platform.history_management.serializers.parent_serializer import GetParentProfileHistorySerializer
from open_schools_platform.history_management.serializers.family_serializer import GetFamilyHistorySerializer
from rest_framework.generics import ListAPIView


class UserHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = User.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetUserHistorySerializer

    @swagger_auto_schema(
        operation_description="Get user history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetUserHistorySerializer()}),
                   404: "No such user"},
    )
    def get(self, request, user_id):
        user = get_user(filters={"id": user_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetUserHistorySerializer,
            queryset=get_history(user, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class OrganizationHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Organization.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetOrganizationHistorySerializer

    @swagger_auto_schema(
        operation_description="Get organization history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetOrganizationHistorySerializer()}),
                   404: "No such organization"},
    )
    def get(self, request, organization_id):
        organization = get_organization(filters={"id": organization_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetOrganizationHistorySerializer,
            queryset=get_history(organization, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class EmployeeHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Employee.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetEmployeeHistorySerializer

    @swagger_auto_schema(
        operation_description="Get employee history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetEmployeeHistorySerializer()}),
                   404: "No such employee"},
    )
    def get(self, request, employee_id):
        employee = get_employee(filters={"id": employee_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetEmployeeHistorySerializer,
            queryset=get_history(employee, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class CircleHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Circle.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetCircleHistorySerializer

    @swagger_auto_schema(
        operation_description="Get circle history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetCircleHistorySerializer()}),
                   404: "No such circle"},
    )
    def get(self, request, circle_id):
        circle = get_circle(filters={"id": circle_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetCircleHistorySerializer,
            queryset=get_history(circle, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class StudentHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Student.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetStudentHistorySerializer

    @swagger_auto_schema(
        operation_description="Get student history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetStudentHistorySerializer()}),
                   404: "No such student"},
    )
    def get(self, request, student_id):
        student = get_student(filters={"id": student_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetStudentHistorySerializer,
            queryset=get_history(student, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class StudentProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = StudentProfile.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetStudentProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get student-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetStudentProfileHistorySerializer()}),
                   404: "No such student-profile"},
    )
    def get(self, request, student_profile_id):
        student_profile = get_student_profile(filters={"id": student_profile_id}, user=request.user,
                                              empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetStudentProfileHistorySerializer,
            queryset=get_history(student_profile, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class EmployeeProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = EmployeeProfile.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetEmployeeProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get employee-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetEmployeeProfileHistorySerializer()}),
                   404: "No such employeeprofile"},
    )
    def get(self, request, employee_profile_id):
        employee_profile = get_employee_profile(filters={"id": employee_profile_id}, user=request.user,
                                                empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetEmployeeProfileHistorySerializer,
            queryset=get_history(employee_profile, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class ParentProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = ParentProfile.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetParentProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get parent-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetParentProfileHistorySerializer()}),
                   404: "No such parent-profile"},
    )
    def get(self, request, parent_profile_id):
        parent_profile = get_parent_profile(filters={"id": parent_profile_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetParentProfileHistorySerializer,
            queryset=get_history(parent_profile, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class FamilyHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Family.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetFamilyHistorySerializer

    @swagger_auto_schema(
        operation_description="Get family history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetFamilyHistorySerializer()}),
                   404: "No such family"},
    )
    def get(self, request, family_id):
        family = get_family(filters={"id": family_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetFamilyHistorySerializer,
            queryset=get_history(family, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class QueryHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Query.objects.all()
    filterset_class = HistoryFilter
    pagination_class = ApiHistoryListPagination
    serializer_class = GetQueryHistorySerializer

    @swagger_auto_schema(
        operation_description="Get query history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': GetQueryHistorySerializer()}),
                   404: "No such query"},
    )
    def get(self, request, query_id):
        query = get_query(filters={"id": query_id}, user=request.user, empty_exception=True)
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=GetQueryHistorySerializer,
            queryset=get_history(query, request.GET.dict()),
            request=request,
            view=self
        )
        return response
