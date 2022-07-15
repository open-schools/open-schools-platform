from django.contrib.auth.middleware import get_user
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
from rest_framework.response import Response

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.query_management.queries.selectors import get_query
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer
from open_schools_platform.query_management.queries.services import run_sender_handler


class QueryStatusChangeApi(views.APIView):
    @swagger_auto_schema(
        operation_description="Change query status.",
        request_body=QueryStatusSerializer,
        responses={200: QueryStatusSerializer},
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
    )
    def put(self, request):
        query_status_serializer = QueryStatusSerializer(data=request.data)
        query_status_serializer.is_valid(raise_exception=True)

        query = get_query(filters={"id": query_status_serializer.validated_data["id"]})

        run_sender_handler(query, query_status_serializer.validated_data["status"], get_user(request))

        return Response({"detail": "Status was changed", "query": QueryStatusSerializer(query).data}, status=200)
