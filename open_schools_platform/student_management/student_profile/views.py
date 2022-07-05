from django.contrib.auth import get_user
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family
from open_schools_platform.student_management.student_profile.serializers import StudentProfileSerializer
from open_schools_platform.student_management.student_profile.services import can_user_create_student_profile_check, \
    create_student_profile


class StudentProfileApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Creates Student profile via provided age, name and family id \n"
                              "Returns Student profile data",
        request_body=StudentProfileSerializer,
        responses={201: "Family was successfully created", 404: "There is no such parent",
                   403: 'User is not logged in'},
        tags=[SwaggerTags.STUDENT_MANAGEMENT_STUDENT_PROFILE]
    )
    def post(self, request):
        student_profile_serializer = StudentProfileSerializer(data=request.data)
        student_profile_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": student_profile_serializer.validated_data['family']})
        if not family:
            raise NotFound("There is no such family")
        user = get_user(request)
        if not can_user_create_student_profile_check(family=family, user=user):
            raise PermissionDenied
        student_profile = create_student_profile(name=student_profile_serializer.validated_data['name'],
                                                 age=student_profile_serializer.validated_data['age'])
        add_student_profile_to_family(student_profile=student_profile, family=family)
        return Response({"student_profile_id": student_profile.id,
                         "student_profile_data": StudentProfileSerializer(request.data).data}, status=201)
