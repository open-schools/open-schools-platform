from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, ListAPIView

from open_schools_platform.api.pagination import get_paginated_response
from rest_framework.response import Response

from .models import Circle
from .selectors import get_circles

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.circles.serializers import CreateCircleSerializer, CircleSerializer
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.selectors import get_organization
from .filters import CircleFilter
from ...api.pagination import ApiListPagination
from ...common.utils import get_dict_excluding_fields
from ...common.views import swagger_dict_response


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
        organization = get_organization(
            filters={"id": create_circle_serializer.validated_data['organization']},
            empty_exception=True,
            empty_message="There is no such organization"
        )
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
    )
    def get(self, request, *args, **kwargs):
        response = get_paginated_response(
            pagination_class=ApiListPagination,
            serializer_class=CircleSerializer,
            queryset=get_circles(filters=request.GET.dict()),
            request=request,
            view=self
        )
        return response
