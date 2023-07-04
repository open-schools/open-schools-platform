from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.history_management.paginators import ApiHistoryListPagination
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.student_management.students.models import Student, StudentProfile
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.organization_management.employees.selectors import get_employee, get_employee_profile
from open_schools_platform.student_management.students.selectors import get_student, get_student_profile
from open_schools_platform.organization_management.circles.selectors import get_circle
from open_schools_platform.history_management.serializers.user_serializer import UserHistorySerializer
from open_schools_platform.history_management.serializers.organization_serializer import OrganizationHistorySerializer
from open_schools_platform.history_management.serializers.employee_serializer import EmployeeHistorySerializer, \
    EmployeeProfileHistorySerializer
from open_schools_platform.history_management.serializers.circle_serializer import CircleHistorySerializer
from open_schools_platform.history_management.serializers.student_serializer import StudentHistorySerializer, \
    StudentProfileHistorySerializer
from open_schools_platform.history_management.serializers.parent_serializer import ParentProfileHistorySerializer
from open_schools_platform.history_management.serializers.family_serializer import FamilyHistorySerializer
from rest_framework.generics import ListAPIView


class UserHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = User.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = UserHistorySerializer

    @swagger_auto_schema(
        operation_description="Get user history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': UserHistorySerializer()}),
                   404: "No such user"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=UserHistorySerializer,
            queryset=get_user(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class OrganizationHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Organization.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = OrganizationHistorySerializer

    @swagger_auto_schema(
        operation_description="Get organization history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': OrganizationHistorySerializer()}),
                   404: "No such organization"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=OrganizationHistorySerializer,
            queryset=get_organization(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class EmployeeHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Employee.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = EmployeeHistorySerializer

    @swagger_auto_schema(
        operation_description="Get employee history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': EmployeeHistorySerializer()}),
                   404: "No such employee"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=EmployeeHistorySerializer,
            queryset=get_employee(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class CircleHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Circle.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = CircleHistorySerializer

    @swagger_auto_schema(
        operation_description="Get circle history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': CircleHistorySerializer()}),
                   404: "No such circle"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=CircleHistorySerializer,
            queryset=get_circle(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class StudentHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Student.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = StudentHistorySerializer

    @swagger_auto_schema(
        operation_description="Get student history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': StudentHistorySerializer()}),
                   404: "No such student"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=StudentHistorySerializer,
            queryset=get_student(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class StudentProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = StudentProfile.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = StudentProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get student-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': StudentProfileHistorySerializer()}),
                   404: "No such student-profile"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=StudentProfileHistorySerializer,
            queryset=get_student_profile(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class EmployeeProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = EmployeeProfile.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = EmployeeProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get employee-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': EmployeeProfileHistorySerializer()}),
                   404: "No such employeeprofile"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=EmployeeProfileHistorySerializer,
            queryset=get_employee_profile(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class ParentProfileHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = ParentProfile.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = ParentProfileHistorySerializer

    @swagger_auto_schema(
        operation_description="Get parent-profile history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': ParentProfileHistorySerializer()}),
                   404: "No such parent-profile"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=ParentProfileHistorySerializer,
            queryset=get_parent_profile(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response


class FamilyHistoryApi(ApiAuthMixin, ListAPIView):
    queryset = Family.objects.all()
    pagination_class = ApiHistoryListPagination
    serializer_class = FamilyHistorySerializer

    @swagger_auto_schema(
        operation_description="Get family history",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: convert_dict_to_serializer({'results': FamilyHistorySerializer()}),
                   404: "No such family"},
    )
    def get(self, request, pk):
        response = get_paginated_response(
            pagination_class=ApiHistoryListPagination,
            serializer_class=FamilyHistorySerializer,
            queryset=get_family(filters={"id": pk}, user=request.user, empty_exception=True).history.all(),
            request=request,
            view=self
        )
        return response
