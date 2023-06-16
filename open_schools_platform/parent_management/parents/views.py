from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.common.views import convert_dict_to_serializer
from rest_framework.response import Response

from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.query_management.queries.serializers import InviteParentQuerySerializer, \
    StudentProfileQuerySerializer
from open_schools_platform.student_management.students.selectors import get_student_profiles_by_families


class InviteParentQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        responses={200: convert_dict_to_serializer({"results": InviteParentQuerySerializer(many=True)}),
                   404: "There are no queries with such recipient"},
        operation_description="Get all invite-parent queries for parent_profile of current user",
    )
    def get(self, request):
        queries = get_queries(
            filters={'recipient_id': str(request.user.parent_profile.id)},
            empty_exception=True,
            empty_message="There are no queries with such recipient"
        )
        return Response({"results": InviteParentQuerySerializer(queries, many=True).data}, status=200)


class StudentJoinCircleQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        responses={200: convert_dict_to_serializer({"results": StudentProfileQuerySerializer(many=True)})},
        operation_description="Get all student-join-circle queries that are accessible by current user's parent_profile"
    )
    def get(self, request):
        families = get_families(
            filters={"parent_profiles": str(request.user.parent_profile.id)},
            empty_exception=True,
            empty_message="There are no families for request user's parent_profile"
        )
        student_profiles = get_student_profiles_by_families(families)
        queries = get_queries(filters={"sender_ids": form_ids_string_from_queryset(student_profiles)})
        return Response(
            {"results": StudentProfileQuerySerializer(queries, many=True, context={'request': request}).data},
            status=200)
