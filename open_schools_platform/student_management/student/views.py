from django.contrib.auth import get_user
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.student_management.student.serializers import StudentProfileSerializer, \
    StudentProfileUpdateSerializer
from open_schools_platform.student_management.student.services import can_user_interact_with_student_profile_check, \
    create_student_profile, update_student_profile


class StudentProfileApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Creates Student profile via provided age, name and family id \n"
                              "Returns Student profile data",
        request_body=StudentProfileSerializer,
        responses={201: "Family was successfully created", 404: "There is no such family",
                   403: "Current user do not have permission to perform this action"},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS]
    )
    def post(self, request):
        student_profile_serializer = StudentProfileSerializer(data=request.data)
        student_profile_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": student_profile_serializer.validated_data['family']})
        if not family:
            raise NotFound("There is no such family")
        user = get_user(request)
        if not can_user_interact_with_student_profile_check(family=family, user=user):
            raise PermissionDenied
        student_profile = create_student_profile(name=student_profile_serializer.validated_data['name'],
                                                 age=student_profile_serializer.validated_data['age'])
        add_student_profile_to_family(student_profile=student_profile, family=family)
        return Response({"student_profile_id": student_profile.id,
                         "student_profile_data": StudentProfileSerializer(request.data).data}, status=201)

    @swagger_auto_schema(
        operation_description="Update student profile",
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENTS],
        request_body=StudentProfileUpdateSerializer,
        responses={200: "Updated student profile data", 404: "There is no such student profile or family",
                   403: "Current user do not have permission to perform this action"}
    )
    def put(self, request):
        student_profile_update_serializer = StudentProfileUpdateSerializer(data=request.data)
        student_profile_update_serializer.is_valid(raise_exception=True)
        student_profile = get_student_profile(
            filters={'id': student_profile_update_serializer.validated_data['student_profile']})
        if not student_profile:
            raise NotFound("There is no such student_profile")
        user = get_user(request)
        if student_profile_update_serializer.validated_data['family']:
            family = get_family(filters={"id": student_profile_update_serializer.validated_data['family']})
            if not family:
                raise NotFound('There is no such family')
            if not can_user_interact_with_student_profile_check(family=family, user=user):
                raise PermissionDenied
        elif student_profile.user != user:
            raise PermissionDenied
        update_student_profile(student_profile=student_profile,
                               name=student_profile_update_serializer.validated_data['name'],
                               age=student_profile_update_serializer.validated_data['age'])
        return Response({"student_profile_id": student_profile.id,
                         "student_profile_name": student_profile.name,
                         "student_profile_age": student_profile.age})
