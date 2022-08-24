from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from django.contrib.gis.measure import D
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING

from open_schools_platform.api.pagination import get_paginated_response
from rest_framework.response import Response

from .models import Circle
from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.circles.serializers import CreateCircleSerializer, CircleSerializer
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.selectors import get_organization
from .filters import CircleFilter
from .selectors import get_circle
from ...api.pagination import ApiListPagination
from ...common.utils import get_dict_excluding_fields
from ...common.views import swagger_dict_response
from ...query_management.queries.selectors import get_queries
from ...query_management.queries.serializers import StudentProfileQuerySerializer
from ...student_management.students.serializers import StudentSerializer


class CreateCircleApi(ApiAuthMixin, CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create circle via provided name and organization.",
        request_body=CreateCircleSerializer,
        responses={201: swagger_dict_response({"circle": CircleSerializer()}), 404: "There is no such organization"},
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


class GetCirclesApi(ApiAuthMixin, ListAPIView):
    queryset = Circle.objects.all()
    filterset_class = CircleFilter
    pagination_class = ApiListPagination
    serializer_class = CircleSerializer

    @swagger_auto_schema(
        operation_description="Get all circles",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        manual_parameters=[
            Parameter('user_location', IN_QUERY, required=False, type=TYPE_STRING),  # type:ignore
        ],
    )
    def get(self, request, *args, **kwargs):
        queryset = Circle.objects.all()
        if 'user_location' in request.GET.dict():
            queryset = queryset.filter(location__distance_lte=(
                request.GET.dict()['user_location'], D(km=CommonConstants.SEARCH_RADIUS))
            )
        response = get_paginated_response(
            pagination_class=ApiListPagination,
            serializer_class=CircleSerializer,
            queryset=CircleFilter(request.GET.dict(), queryset).qs,
            request=request,
            view=self
        )
        return response


class GetCircleApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get circle with provided UUID",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: swagger_dict_response({"circle": CircleSerializer()}), 404: "There is no such circle"}
    )
    def get(self, request, pk):
        circle = get_circle(filters={"id": str(pk)})
        if not circle:
            raise NotFound("There is no such circle")
        return Response({"circle": CircleSerializer(circle).data}, status=200)


class CirclesQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all queries for provided circle.",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: swagger_dict_response({"results": StudentProfileQuerySerializer(many=True)})}
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
    @swagger_auto_schema(
        operation_description="Get students in this circle",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        responses={200: swagger_dict_response({"results": StudentSerializer(many=True)})}
    )
    def get(self, request, pk):
        circle = get_circle(filters={"id": str(pk)}, user=request.user)
        qs = circle.students.all()
        return Response({"results": StudentSerializer(qs, many=True).data}, status=200)
