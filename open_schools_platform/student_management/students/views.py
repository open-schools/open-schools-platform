from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import get_dict_excluding_fields
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.circles.selectors import get_circle, get_circles_by_students
from open_schools_platform.organization_management.circles.serializers import CircleSerializer
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family
from open_schools_platform.query_management.queries.selectors import get_queries, get_query_with_checks
from open_schools_platform.query_management.queries.serializers import StudentProfileQuerySerializer
from open_schools_platform.student_management.students.selectors import get_student_profile, get_students, get_student
from open_schools_platform.student_management.students.serializers import StudentProfileCreateSerializer, \
    StudentProfileUpdateSerializer, StudentProfileSerializer, AutoStudentJoinCircleQuerySerializer, \
    StudentJoinCircleQueryUpdateSerializer, StudentJoinCircleQuerySerializer, StudentProfileAddPhotoSerializer
from open_schools_platform.student_management.students.services import \
    create_student_profile, update_student_profile, update_student_join_circle_body, \
    autogenerate_family_logic, query_creation_logic


class StudentProfileApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Student profile via provided age, name and family id \n"
                              "Returns Student profile data",
        request_body=StudentProfileCreateSerializer,
        responses={201: convert_dict_to_serializer({"student_profile": StudentProfileSerializer()}),
                   404: "No such family",
                   403: "Current user do not have permission to perform this action"},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS]
    )
    def post(self, request):
        student_profile_serializer = StudentProfileCreateSerializer(data=request.data)
        student_profile_serializer.is_valid(raise_exception=True)
        family = get_family(
            filters={"id": str(student_profile_serializer.validated_data['family'])},
            user=request.user,
            empty_exception=True,
        )
        student_profile = create_student_profile(
            **get_dict_excluding_fields(student_profile_serializer.validated_data, ["family"]))
        add_student_profile_to_family(student_profile=student_profile, family=family)
        return Response({"student_profile": StudentProfileSerializer(student_profile).data}, status=201)


class StudentProfileAddPhotoApi(ApiAuthMixin, APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Adds photo to provided student profile",
        request_body=StudentProfileAddPhotoSerializer,
        responses={200: convert_dict_to_serializer({"student_profile": StudentProfileSerializer()}),
                   404: "No such student profile",
                   403: "Current user do not have permission to perform this action"},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS]
    )
    def post(self, request, pk):
        add_photo_serializer = StudentProfileAddPhotoSerializer(data=request.data)
        add_photo_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(filters={"id": str(pk)}, user=request.user,
                                              empty_exception=True)
        update_student_profile(student_profile=student_profile,
                               data=add_photo_serializer.validated_data)
        return Response({"student_profile": StudentProfileSerializer(student_profile).data}, status=201)


class StudentProfileUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update student profile",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentProfileUpdateSerializer(),
        responses={200: convert_dict_to_serializer({"student_profile": StudentProfileSerializer()}),
                   404: "No such student profile or family",
                   403: "Current user do not have permission to perform this action"}
    )
    def patch(self, request, pk):
        student_profile_update_serializer = StudentProfileUpdateSerializer(data=request.data)
        student_profile_update_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(
            filters={'id': str(pk)},
            user=request.user,
            empty_exception=True,
        )

        if student_profile_update_serializer.validated_data['family']:
            get_family(
                filters={"id": student_profile_update_serializer.validated_data['family']},
                user=request.user,
                empty_exception=True,
            )
        update_student_profile(student_profile=student_profile,
                               data=get_dict_excluding_fields(student_profile_update_serializer.validated_data, []))
        return Response({"student_profile": StudentProfileSerializer(student_profile).data}, status=200)


class StudentProfileDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        operation_description="Delete student-profile.",
        responses={204: "Successful deletion", 404: "No such student-profile"}
    )
    def delete(self, request, pk):
        student_profile = get_student_profile(filters={'id': pk}, empty_exception=True, user=request.user)
        student_profile.delete()
        return Response(status=204)


class AutoStudentJoinCircleQueryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates student profile, student and family.\n"
                              "Forms query for adding created student to circle",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=AutoStudentJoinCircleQuerySerializer(),
        responses={201: convert_dict_to_serializer({"query": StudentProfileQuerySerializer()}),
                   406: "Current user already has family"}
    )
    def post(self, request):
        student_join_circle_req_serializer = AutoStudentJoinCircleQuerySerializer(data=request.data)
        student_join_circle_req_serializer.is_valid(raise_exception=True)
        if get_family(filters={"parent_profiles": str(request.user.parent_profile.id)}, user=request.user):
            raise NotAcceptable("Please choose already created family")

        student_profile = autogenerate_family_logic(student_join_circle_req_serializer.validated_data, request.user)

        circle = get_circle(
            filters={'id': student_join_circle_req_serializer.validated_data["circle"]},
            empty_exception=True,
        )

        query = query_creation_logic(student_join_circle_req_serializer.validated_data, circle,
                                     student_profile, request.user)

        return Response({"query": StudentProfileQuerySerializer(query).data}, status=201)


class StudentJoinCircleQueryApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Forms query for adding created student to circle",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentJoinCircleQuerySerializer(),
        responses={201: convert_dict_to_serializer({"query": StudentProfileQuerySerializer()}),
                   404: "No such student profile"}
    )
    def post(self, request, pk):
        student_join_circle_req_serializer = StudentJoinCircleQuerySerializer(data=request.data)
        student_join_circle_req_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(
            filters={"id": str(pk)},
            user=request.user,
            empty_exception=True,
        )

        circle = get_circle(
            filters={'id': student_join_circle_req_serializer.validated_data["circle"]},
            empty_exception=True,
        )

        query = query_creation_logic(student_join_circle_req_serializer.validated_data, circle,
                                     student_profile, request.user)
        return Response({"query": StudentProfileQuerySerializer(query).data}, status=201)


class StudentJoinCircleQueryUpdateApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update body of student join circle query",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentJoinCircleQueryUpdateSerializer(),
        responses={201: convert_dict_to_serializer({"query": StudentProfileQuerySerializer()}),
                   404: "No such query",
                   406: "Cant update query because it's status is not SENT"}
    )
    def patch(self, request):
        query_update_serializer = StudentJoinCircleQueryUpdateSerializer(data=request.data)
        query_update_serializer.is_valid(raise_exception=True)

        query = get_query_with_checks(
            update_query_check=True,
            pk=str(query_update_serializer.validated_data["query"]),
            user=request.user,
        )
        update_student_join_circle_body(
            query=query,
            data=query_update_serializer.validated_data["body"],
        )
        return Response({"query": StudentProfileQuerySerializer(query).data}, status=200)


class StudentQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        responses={200: convert_dict_to_serializer({"results": StudentProfileQuerySerializer(many=True)})},
        operation_description="Get all queries for provided student profile",
    )
    def get(self, request, pk):
        get_student_profile(
            filters={'id': str(pk)},
            empty_exception=True,
            empty_message='There is no such student profile'
        )

        student_profile = get_student_profile(filters={"id": str(pk)}, user=request.user)
        queries = get_queries(
            filters={'sender_id': str(student_profile.id)},
            empty_exception=True,
            empty_message='There are no queries with such sender'
        )
        return Response({"results": StudentProfileQuerySerializer(queries, many=True).data}, status=200)


class StudentCirclesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        responses={200: convert_dict_to_serializer({"results": CircleSerializer(many=True)})},
        operation_description="Get all circles for provided student profile",
    )
    def get(self, request, pk):
        student_profile = get_student_profile(
            filters={"id": str(pk)},
            user=request.user,
            empty_exception=True,
        )
        students = get_students(
            filters={'student_profile': str(student_profile.id)},
        )
        circles = get_circles_by_students(students=students)
        return Response({"results": CircleSerializer(circles, many=True).data}, status=200)


class StudentDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        operation_description="Delete student.",
        responses={204: "Successful deletion", 404: "No such student"}
    )
    def delete(self, request, pk):
        student = get_student(filters={'id': pk}, empty_exception=True, user=request.user)
        student.delete()
        return Response(status=204)
