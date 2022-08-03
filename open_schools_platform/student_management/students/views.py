from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import get_dict_excluding_fields
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.organization_management.circles.selectors import get_circle, get_circles_by_students
from open_schools_platform.organization_management.circles.serializers import CircleSerializer
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family, create_family
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import StudentProfileQuerySerializer
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.selectors import get_student_profile, get_students
from open_schools_platform.student_management.students.serializers import StudentProfileCreateSerializer, \
    StudentProfileUpdateSerializer, StudentProfileSerializer, AutoStudentJoinCircleQuerySerializer, \
    StudentJoinCircleQueryUpdateSerializer, StudentJoinCircleQuerySerializer
from open_schools_platform.student_management.students.services import \
    create_student_profile, update_student_profile, create_student, update_student_join_circle_body


class StudentProfileApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Student profile via provided age, name and family id \n"
                              "Returns Student profile data",
        request_body=StudentProfileCreateSerializer,
        responses={201: swagger_dict_response({"student_profile": StudentProfileSerializer()}),
                   404: "There is no such family",
                   403: "Current user do not have permission to perform this action"},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS]
    )
    def post(self, request):
        student_profile_serializer = StudentProfileCreateSerializer(data=request.data)
        student_profile_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": str(student_profile_serializer.validated_data['family'])}, user=request.user)
        if not family:
            raise NotFound("There is no such family")
        student_profile = create_student_profile(name=student_profile_serializer.validated_data['name'],
                                                 age=student_profile_serializer.validated_data['age'])
        add_student_profile_to_family(student_profile=student_profile, family=family)
        return Response({"student_profile": StudentProfileSerializer(student_profile).data}, status=201)


class StudentProfileUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update student profile",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentProfileUpdateSerializer(),
        responses={200: swagger_dict_response({"student_profile": StudentProfileSerializer()}),
                   404: "There is no such student profile or family",
                   403: "Current user do not have permission to perform this action"}
    )
    def put(self, request, pk):
        student_profile_update_serializer = StudentProfileUpdateSerializer(data=request.data)
        student_profile_update_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(
            filters={'id': str(pk)},
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
        return Response({"student_profile": StudentProfileSerializer(student_profile).data}, status=200)


class AutoStudentJoinCircleQueryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates student profile, student and family.\n"
                              "Forms query for adding created student to circle",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=AutoStudentJoinCircleQuerySerializer(),
        responses={201: swagger_dict_response({"query": StudentProfileQuerySerializer()}),
                   406: "Current user already has family"}
    )
    def post(self, request):
        student_join_circle_req_serializer = AutoStudentJoinCircleQuerySerializer(data=request.data)
        student_join_circle_req_serializer.is_valid(raise_exception=True)
        if get_family(filters={"parent_profiles": str(request.user.parent_profile.id)}, user=request.user):
            raise NotAcceptable("Please choose already created family")
        student_profile = create_student_profile(name=student_join_circle_req_serializer.validated_data["name"],
                                                 age=student_join_circle_req_serializer.validated_data["age"])
        family = create_family(parent=request.user.parent_profile)
        add_student_profile_to_family(family=family, student_profile=student_profile)
        student = create_student(name=student_profile.name)
        circle = get_circle(filters={'id': student_join_circle_req_serializer.validated_data["circle"]})
        if not circle:
            raise NotFound('There is no such circle')
        query = create_query(
            sender_model_name="studentprofile", sender_id=student_profile.id,
            recipient_model_name="circle", recipient_id=circle.id,
            body_model_name="student", body_id=student.id
        )

        return Response({"query": StudentProfileQuerySerializer(query).data}, status=201)


class StudentJoinCircleQueryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Forms query for adding created student to circle",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentJoinCircleQuerySerializer(),
        responses={201: swagger_dict_response({"query": StudentProfileQuerySerializer()}),
                   404: "There is no such student profile"}
    )
    def post(self, request, pk):
        student_join_circle_req_serializer = StudentJoinCircleQuerySerializer(data=request.data)
        student_join_circle_req_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(filters={"id": str(pk)}, user=request.user)
        if not student_profile:
            raise NotFound("There is no such student profile")
        student = create_student(name=student_profile.name)
        circle = get_circle(filters={'id': student_join_circle_req_serializer.validated_data["circle"]})
        if not circle:
            raise NotFound('There is no such circle')
        query = create_query(
            sender_model_name="studentprofile", sender_id=student_profile.id,
            recipient_model_name="circle", recipient_id=circle.id,
            body_model_name="student", body_id=student.id
        )
        return Response({"query": StudentProfileQuerySerializer(query).data}, status=201)


class StudentJoinCircleQueryUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update body of student join circle query",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentJoinCircleQueryUpdateSerializer(),
        responses={201: swagger_dict_response({"query": StudentProfileQuerySerializer()}),
                   404: "There is no such query",
                   406: "Cant update query because it's status is not SENT"}
    )
    def put(self, request):
        query_update_serializer = StudentJoinCircleQueryUpdateSerializer(data=request.data)
        query_update_serializer.is_valid(raise_exception=True)

        query = get_query_with_checks(
            pk=str(query_update_serializer.validated_data["query"]),
            user=request.user,
            update_query_check=True
        )
        update_student_join_circle_body(
            query=query,
            data=get_dict_excluding_fields(query_update_serializer.validated_data, ["query"])
        )
        return Response({"query": StudentProfileQuerySerializer(query).data}, status=200)


class StudentQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        responses={200: swagger_dict_response({"results": StudentProfileQuerySerializer(many=True)})},
        operation_description="Get all queries for provided student profile",
    )
    def get(self, request, pk):
        if not get_student_profile(filters={'id': str(pk)}):
            raise NotFound('There is no such student profile')
        student_profile = get_student_profile(filters={"id": str(pk)}, user=request.user)
        queries = get_queries(filters={'sender_id': str(student_profile.id)})
        if not queries:
            raise NotFound('There are no queries with such sender')
        return Response({"results": StudentProfileQuerySerializer(queries, many=True).data}, status=200)


class StudentCirclesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        responses={200: swagger_dict_response({"results": CircleSerializer(many=True)})},
        operation_description="Get all circles for provided student profile",
    )
    def get(self, request, pk):
        if not get_student_profile(filters={'id': str(pk)}):
            raise NotFound('There is no such student profile')
        student_profile = get_student_profile(filters={"id": str(pk)}, user=request.user)
        students = get_students(filters={'student_profile': str(student_profile.id)})
        circles = get_circles_by_students(students=students)
        if not students:
            raise NotFound('There are no students with such student_profile')
        if not circles:
            raise NotFound('Such student profile does not have any circles')
        return Response({"results": CircleSerializer(circles, many=True).data}, status=200)
