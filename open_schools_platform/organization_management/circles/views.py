from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView

from open_schools_platform.api.pagination import get_paginated_response
from rest_framework.response import Response

from .selectors import get_circles, get_circle

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.circles.serializers import CreateCircleSerializer, CircleSerializer
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.selectors import get_organization
from .filters import CircleFilter
from ...api.pagination import ApiListPagination
from ...common.utils import get_dict_excluding_fields
from ...query_management.queries.selectors import get_queries
from ...query_management.queries.serializers import StudentProfileQuerySerializer
from ...student_management.students.serializers import StudentSerializer


class CreateCircleApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create circle via provided name and organization.",
        request_body=CreateCircleSerializer,
        responses={201: CircleSerializer, 404: "There is no such organization"},
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
    )
    def post(self, request):
        create_circle_serializer = CreateCircleSerializer(data=request.data)
        create_circle_serializer.is_valid(raise_exception=True)
        organization = get_organization(filters={"id": create_circle_serializer.validated_data['organization']})
        if not organization:
            raise NotFound("There is no such organization")
        circle = create_circle(**get_dict_excluding_fields(create_circle_serializer.validated_data, ["organization"]),
                               organization=organization)
        return Response({"circle": CircleSerializer(circle).data}, status=201)


class GetCircles(ApiAuthMixin, ListAPIView):
    filterset_class = CircleFilter
    pagination_class = ApiListPagination
    serializer_class = CircleSerializer

    @swagger_auto_schema(
        operation_description="Get all circles",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
    )
    def get(self, request):
        circles = get_circles()

        response = get_paginated_response(
            pagination_class=ApiListPagination,
            serializer_class=CircleSerializer,
            queryset=circles,
            request=request,
            view=self
        )
        return response


class CirclesQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all queries for provided circle.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
    )
    def get(self, request, pk):
        circle = get_circle(filters={"id": str(pk)}, user=request.user)
        if not circle:
            raise NotFound("There is no such circle.")
        queries = get_queries(filters={"recipient_id": str(pk)})
        if not queries:
            raise NotFound("There are no queries with such recipient.")
        return Response({"results": StudentProfileQuerySerializer(queries, many=True).data}, status=200)


class CirclesStudentsListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(operation_description="Get students in this circle",
                         tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
                         )
    def get(self, request, pk):
        circle = get_circle(filters={"id": str(pk)}, user=request.user)
        qs = circle.students.all()
        return Response({"results": StudentSerializer(qs, many=True).data}, status=200)
