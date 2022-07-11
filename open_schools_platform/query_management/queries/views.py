from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
from rest_framework.response import Response

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import get_dict_including_fields
from open_schools_platform.organization_management.organizations.models import OrganizationManager
from open_schools_platform.query_management.queries.selectors import get_query
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer
from open_schools_platform.query_management.queries.services import query_update, run_sender_handler


class QueryStatusChangeApi(views.APIView):
    @swagger_auto_schema(
        operation_description="Change query status.",
        request_body=QueryStatusSerializer,
        responses={201: QueryStatusSerializer},
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
    )
    def put(self, request):
        query_status_serializer = QueryStatusSerializer(data=request.data)
        query_status_serializer.is_valid(raise_exception=True)

        query = get_query(filters=get_dict_including_fields(query_status_serializer.validated_data, ["id"]))

        run_sender_handler(query, query_status_serializer.validated_data["status"])

        return Response({"detail": "Status was changed"}, status=200)
