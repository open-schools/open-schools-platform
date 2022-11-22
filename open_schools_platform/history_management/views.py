from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.organization_management.employees.selectors import get_employee
from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.history_management.serializers.user_serializer import UserHistorySerializer
from open_schools_platform.history_management.serializers.organization_serializer import OrganizationHistorySerializer
from open_schools_platform.history_management.serializers.employee_serializer import EmployeeHistorySerializer
from open_schools_platform.history_management.serializers.circle_serializer import CircleHistorySerializer
from open_schools_platform.history_management.serializers.student_serializer import StudentHistorySerializer

from ..organization_management.circles.selectors import get_circle
from ..student_management.students.selectors import get_student


class UserHistoryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get user history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': UserHistorySerializer(many=True)}),
                   404: "There is no such user"},
    )
    def get(self, request, pk):
        user = get_user(filters={"id": pk},
                        user=request.user,
                        empty_exception=True,
                        empty_message="There is no such user")
        return Response({"results": UserHistorySerializer(user).data}, status=200)


class OrganizationHistoryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get organization history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': OrganizationHistorySerializer(many=True)}),
                   404: "There is no such organization"},
    )
    def get(self, request, pk):
        organization = get_organization(filters={"id": pk},
                                        user=request.user,
                                        empty_exception=True,
                                        empty_message="There is no such organization")
        return Response({"results": OrganizationHistorySerializer(organization).data}, status=200)


class EmployeeHistoryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get employee history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': EmployeeHistorySerializer(many=True)}),
                   404: "There is no such employee"},
    )
    def get(self, request, pk):
        employee = get_employee(filters={"id": pk},
                                user=request.user,
                                empty_exception=True,
                                empty_message="There is no such employee")
        return Response({"results": EmployeeHistorySerializer(employee).data}, status=200)


class CircleHistoryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get circle history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': CircleHistorySerializer(many=True)}),
                   404: "There is no such circle"},
    )
    def get(self, request, pk):
        circle = get_circle(filters={"id": pk},
                            user=request.user,
                            empty_exception=True,
                            empty_message="There is no such circle")
        return Response({"results": CircleHistorySerializer(circle).data}, status=200)


class StudentHistoryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get student history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': StudentHistorySerializer(many=True)}),
                   404: "There is no such student"},
    )
    def get(self, request, pk):
        student = get_student(filters={"id": pk},
                              user=request.user,
                              empty_exception=True,
                              empty_message="There is no such student")
        return Response({"results": StudentHistorySerializer(student).data}, status=200)
