from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.teachers.selectors import get_teacher_profile
from open_schools_platform.organization_management.teachers.serializers import GetTeacherProfileSerializer
from rest_framework.response import Response


class GetTeacherProfileApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get teacher_profile with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_TEACHERS],
        responses={200: convert_dict_to_serializer({"teacher_profile": GetTeacherProfileSerializer()})}
    )
    def get(self, request, teacher_profile_id):
        teacher_profile = get_teacher_profile(filters={"id": str(teacher_profile_id)}, empty_exception=True,
                                              user=request.user)
        return Response(
            {"teacher_profile": GetTeacherProfileSerializer(teacher_profile, context={'request': request}).data},
            status=200)
