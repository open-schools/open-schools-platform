from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import get_dict_excluding_fields
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family, create_family
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.selectors import get_student_profile
from open_schools_platform.student_management.students.serializers import StudentProfileCreateSerializer, \
    StudentProfileUpdateSerializer, StudentProfileSerializer, StudentJoinCircleQuerySerializer
from open_schools_platform.student_management.students.services import \
    create_student_profile, update_student_profile, create_student


class StudentProfileApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Student profile via provided age, name and family id \n"
                              "Returns Student profile data",
        request_body=StudentProfileCreateSerializer,
        responses={201: StudentProfileSerializer, 404: "There is no such family",
                   403: "Current user do not have permission to perform this action"},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS]
    )
    def post(self, request):
        student_profile_serializer = StudentProfileCreateSerializer(data=request.data)
        student_profile_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": student_profile_serializer.validated_data['family']}, user=request.user)
        if not family:
            raise NotFound("There is no such family")
        student_profile = create_student_profile(name=student_profile_serializer.validated_data['name'],
                                                 age=student_profile_serializer.validated_data['age'])
        add_student_profile_to_family(student_profile=student_profile, family=family)
        return Response(StudentProfileSerializer(student_profile).data, status=201)

    @swagger_auto_schema(
        operation_description="Update students profile",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentProfileUpdateSerializer(),
        responses={200: StudentProfileSerializer, 404: "There is no such students profile or family",
                   403: "Current user do not have permission to perform this action"}
    )
    def put(self, request):
        student_profile_update_serializer = StudentProfileUpdateSerializer(data=request.data)
        student_profile_update_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(
            filters={'id': student_profile_update_serializer.validated_data['student_profile']},
            user=request.user,
        )
        if not student_profile:
            raise NotFound("There is no such student_profile")

        if student_profile_update_serializer.validated_data['family']:
            family = get_family(filters={"id": student_profile_update_serializer.validated_data['family']},
                                user=request.user)
            if not family:
                raise NotFound('There is no such family')
        update_student_profile(student_profile=student_profile,
                               data=get_dict_excluding_fields(student_profile_update_serializer.validated_data,
                                                              ['student_profile', 'family']))
        return Response(StudentProfileSerializer(student_profile).data, status=200)


class StudentJoinCircleQueryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates students profile, students and family.\n"
                              "Forms query for adding created students to circle",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentJoinCircleQuerySerializer(),
        responses={201: QueryStatusSerializer, 406: "Current user already has family"}
    )
    def post(self, request, pk):
        student_join_circle_req_serializer = StudentJoinCircleQuerySerializer(data=request.data)
        student_join_circle_req_serializer.is_valid(raise_exception=True)
        user = request.user

        if get_family(filters={"parent_profiles": str(user.parent_profile.id)}, user=request.user):
            raise NotAcceptable("Please choose already created family")
        student_profile = create_student_profile(name=student_join_circle_req_serializer.validated_data["name"],
                                                 age=student_join_circle_req_serializer.validated_data["age"])
        family = create_family(parent=request.user.parent_profile)
        add_student_profile_to_family(family=family, student_profile=student_profile)
        student = create_student(name=student_profile.name)

        query = create_query(sender_model_name="studentprofile", sender_id=student_profile.id,
                             recipient_model_name="circle", recipient_id=pk,
                             body_model_name="students", body_id=student.id)

        return Response(QueryStatusSerializer(query).data, status=201)
