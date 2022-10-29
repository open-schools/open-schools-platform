from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from rest_framework.response import Response

from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.query_management.queries.serializers import InviteParentQuerySerializer


class InviteParentQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        responses={200: swagger_dict_response({"results": InviteParentQuerySerializer(many=True)}),
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
