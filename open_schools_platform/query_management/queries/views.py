from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.query_management.queries.selectors import get_query, get_queries
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer, QuerySerializer
from open_schools_platform.query_management.queries.services import run_sender_handler


class QueryStatusChangeApi(ApiAuthMixin, views.APIView):
    @swagger_auto_schema(
        operation_description="Change query status.",
        request_body=QueryStatusSerializer,
        responses={200: QueryStatusSerializer},
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
    )
    def put(self, request):
        query_status_serializer = QueryStatusSerializer(data=request.data)
        query_status_serializer.is_valid(raise_exception=True)
        query = get_query(filters={"id": query_status_serializer.validated_data["id"]}, user=request.user)

        query = run_sender_handler(query, query_status_serializer.validated_data["status"], request.user)

        return Response({"detail": "Status was changed", "query": QueryStatusSerializer(query).data}, status=200)


class QueryListApi(ApiAuthMixin, ListAPIView):

    def get_organization_queries(self, request, organization):
        serializer_class = QuerySerializer
        if not get_organization(filters={'id': str(organization)}):
            raise NotFound('There is no such organization')
        queries = get_queries(filters={'sender_id': str(organization)}, user=request.user)
        if not queries:
            raise NotFound('There are no queries with such sender')
        serializer = serializer_class(queries, many=True)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        tags=[SwaggerTags.QUERY_MANAGEMENT_QUERIES],
        operation_description="Return paginated list of employees.",
        manual_parameters=[
            Parameter('organization', IN_QUERY, required=False, type=TYPE_STRING),   # type: ignore
            Parameter('student_profile', IN_QUERY, required=False, type=TYPE_STRING),   # type: ignore
        ],
    )
    def get(self, request, *args, **kwargs):
        response = []
        if self.request.query_params.get('organization'):
            response = self.get_organization_queries(organization=self.request.query_params.get('organization'),
                                                     request=request)
        return response

