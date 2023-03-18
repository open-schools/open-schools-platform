from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView

from open_schools_platform.api.pagination import get_paginated_response
from rest_framework.response import Response
from .models import Circle

from open_schools_platform.api.mixins import ApiAuthMixin, XLSXMixin, ICalMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.circles.serializers import CreateCircleSerializer, \
    CircleSerializer, CircleStudentInviteSerializer, CircleListSerializer
from open_schools_platform.organization_management.circles.services import create_circle, \
    is_organization_related_to_student_profile, generate_ical
from open_schools_platform.organization_management.organizations.selectors import get_organization
from .filters import CircleFilter
from .paginators import ApiCircleListPagination
from .selectors import get_circle, get_circles
from ..teachers.selectors import get_teacher_profile
from ..teachers.serializers import CircleTeacherInviteSerializer
from ..teachers.services import create_teacher
from ...common.utils import get_dict_excluding_fields
from ...common.views import convert_dict_to_serializer
from ...parent_management.families.selectors import get_families
from ...parent_management.parents.services import get_parent_profile_or_create_new_user, \
    get_parent_family_or_create_new
from ...query_management.queries.selectors import get_queries
from ...query_management.queries.serializers import StudentProfileQuerySerializer, QueryStatusSerializer
from ...query_management.queries.services import create_query
from ...student_management.students.selectors import get_students
from ...student_management.students.serializers import StudentSerializer
from ...student_management.students.services import create_student, get_student_profile_by_family_or_create_new, \
    export_students


class CreateCircleApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create circle via provided name and organization.",
        request_body=CreateCircleSerializer,
        responses={201: convert_dict_to_serializer({"circle": CircleSerializer()}), 404: "No such organization"},
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
    )
    def post(self, request):
        create_circle_serializer = CreateCircleSerializer(data=request.data)
        create_circle_serializer.is_valid(raise_exception=True)
        organization = get_organization(
            filters={"id": create_circle_serializer.validated_data['organization']},
            user=request.user,
            empty_exception=True,
        )
        circle = create_circle(**get_dict_excluding_fields(create_circle_serializer.validated_data, ["organization"]),
                               organization=organization)
        return Response({"circle": CircleSerializer(circle).data}, status=201)


class GetCirclesApi(ApiAuthMixin, ListAPIView):
    queryset = Circle.objects.all()
    filterset_class = CircleFilter
    pagination_class = ApiCircleListPagination
    serializer_class = CircleListSerializer

    @swagger_auto_schema(
        operation_description="Get all circles",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
    )
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        if 'student_profile' in data.keys():
            if 'organization' not in data.keys():
                raise ValidationError("Organization is not defined")
            if not is_organization_related_to_student_profile(
                    data["organization"], data["student_profile"], request.user):
                raise PermissionDenied("This organization is not related to this student_profile")

        response = get_paginated_response(
            pagination_class=ApiCircleListPagination,
            serializer_class=CircleListSerializer,
            queryset=get_circles(filters=request.GET.dict()),
            request=request,
            view=self
        )
        return response


class GetCircleApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get circle with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: convert_dict_to_serializer({"circle": CircleSerializer()})}
    )
    def get(self, request, pk):
        circle = get_circle(
            filters={"id": str(pk)},
            empty_exception=True,
        )
        return Response({"circle": CircleSerializer(circle).data}, status=200)


class CirclesQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all queries for provided circle.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: convert_dict_to_serializer({"results": StudentProfileQuerySerializer(many=True)})}
    )
    def get(self, request, pk):
        get_circle(
            filters={"id": str(pk)},
            user=request.user,
            empty_exception=True,
        )
        queries = get_queries(
            filters={"recipient_id": str(pk)},
            empty_exception=True,
        )
        return Response(
            {"results": StudentProfileQuerySerializer(queries, many=True, context={'request': request}).data},
            status=200)


class CirclesStudentsListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get students in this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: convert_dict_to_serializer({"results": StudentSerializer(many=True)})}
    )
    def get(self, request, pk):
        circle = get_circle(filters={"id": str(pk)}, user=request.user, empty_exception=True)
        qs = circle.students.all()
        return Response({"results": StudentSerializer(qs, many=True, context={'request': request}).data}, status=200)


class CircleDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        operation_description="Delete circle.",
        responses={204: "Successfully deleted", 404: "No such circle"}
    )
    def delete(self, request, pk):
        circle = get_circle(filters={'id': str(pk)}, empty_exception=True, user=request.user)
        circle.delete()
        return Response(status=204)


class InviteStudentApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        request_body=CircleStudentInviteSerializer,
        responses={201: convert_dict_to_serializer({"query": QueryStatusSerializer()})},
        operation_description="Creates invite student query.",
    )
    def post(self, request, pk) -> Response:
        invite_serializer = CircleStudentInviteSerializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)

        circle = get_circle(filters={"id": pk}, user=request.user, empty_exception=True)
        parent_phone = invite_serializer.validated_data["parent_phone"]
        student_phone = invite_serializer.validated_data["student_phone"]
        email = invite_serializer.validated_data["email"]
        name = invite_serializer.validated_data["body"]["name"]

        parent_profile = get_parent_profile_or_create_new_user(phone=str(parent_phone), email=str(email),
                                                               circle=circle)
        family = get_parent_family_or_create_new(parent_profile=parent_profile)
        student_profile = get_student_profile_by_family_or_create_new(student_phone=student_phone, student_name=name,
                                                                      families=parent_profile.families.all())
        student = create_student(**invite_serializer.validated_data["body"])
        get_families()

        query = create_query(sender_model_name="circle", sender_id=pk,
                             recipient_model_name="family", recipient_id=family.id,
                             body_model_name="student", body_id=student.id,
                             additional_model_name="studentprofile", additional_id=student_profile.id)

        return Response({"query": QueryStatusSerializer(query).data}, status=201)


class InviteTeacherApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        request_body=CircleTeacherInviteSerializer,
        responses={201: convert_dict_to_serializer({"query": QueryStatusSerializer()})},
        operation_description="Creates invite teacher query.",
    )
    def post(self, request, pk) -> Response:
        invite_serializer = CircleTeacherInviteSerializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)

        get_circle(filters={"id": pk}, user=request.user, empty_exception=True)
        phone = invite_serializer.validated_data["phone"]

        teacher_profile = get_teacher_profile(filters={'phone': str(phone)})
        teacher = create_teacher(**invite_serializer.validated_data["body"])

        query = create_query(sender_model_name="circle", sender_id=pk,
                             recipient_model_name="teacherprofile", recipient_id=teacher_profile.id,
                             body_model_name="teacher", body_id=teacher.id)

        return Response({"query": QueryStatusSerializer(query).data}, status=201)


class CirclesStudentProfilesExportApi(ApiAuthMixin, XLSXMixin, APIView):
    filename = 'circle_students.xlsx'

    @swagger_auto_schema(
        operation_description="Export students from this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))}
    )
    def get(self, request, pk):
        get_circle(filters={'id': str(pk)}, user=request.user, empty_exception=True)
        students = get_students(filters={'circle': str(pk)})
        file = export_students(students, export_format='xlsx')
        return Response(file, status=200)


class CircleICalExportApi(ApiAuthMixin, ICalMixin, APIView):
    filename = 'schedule.ics'

    @swagger_auto_schema(
        operation_description="Exports circle schedule",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))}
    )
    def get(self, request, pk):
        circle = get_circle(filters={'id': str(pk)}, empty_exception=True)
        self.filename = circle.name
        file = generate_ical(circle)
        return Response(file, status=200)


class CirclesICalExportApi(ApiAuthMixin, ICalMixin, ListAPIView):
    filename = 'schedule.ics'
    filterset_class = CircleFilter

    @swagger_auto_schema(
        operation_description="Exports circles schedule",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        filterset_class=CircleFilter,
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))}
    )
    def get(self, request):
        data = request.GET.dict()
        if 'student_profile' in data.keys():
            if 'organization' not in data.keys():
                raise ValidationError("Organization is not defined")
            if not is_organization_related_to_student_profile(
                    data["organization"], data["student_profile"], request.user):
                raise PermissionDenied("This organization is not related to this student_profile")

        circles = get_circles(filters=request.GET.dict())
        file = generate_ical(circles)
        return Response(file, status=200)
