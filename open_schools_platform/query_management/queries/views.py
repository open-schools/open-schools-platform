from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
from rest_framework.response import Response

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.query_management.queries.selectors import get_query, \
    get_query_status_changes
from open_schools_platform.query_management.queries.serializers import GetQueryStatusSerializer, \
    QueryStatusChangesSerializer
from open_schools_platform.query_management.queries.services import run_sender_handler


class QueryStatusChangeApi(ApiAuthMixin, views.APIView):
    @swagger_auto_schema(
        operation_description="Change query status.",
        request_body=GetQueryStatusSerializer,
        responses={200: convert_dict_to_serializer({"query": GetQueryStatusSerializer()})},
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
    )
    def patch(self, request):
        query_status_serializer = GetQueryStatusSerializer(data=request.data)
        query_status_serializer.is_valid(raise_exception=True)
        query = get_query(
            filters={"id": query_status_serializer.validated_data["id"]},
            user=request.user,
            empty_exception=True,
        )

        query = run_sender_handler(query, query_status_serializer.validated_data["status"], request.user)

        return Response({"detail": "Status was changed", "query": GetQueryStatusSerializer(query).data}, status=200)


class QueryChangesHistoryApi(ApiAuthMixin, views.APIView):
    @swagger_auto_schema(
        operation_description="Show changes of query status.",
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
        responses={200: convert_dict_to_serializer({"results": QueryStatusChangesSerializer(many=True)})}
    )
    def get(self, request, query_id):
        query = get_query(filters={"id": query_id},
                          user=request.user,
                          empty_exception=True
                          )
        changes = get_query_status_changes(query)
        return Response(
            {"results": QueryStatusChangesSerializer(changes, many=True, context={'request': request}).data},
            status=200)
