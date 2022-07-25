from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.circles.serializers import CreateCircleSerializer, CircleSerializer
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.selectors import get_organization, \
    get_organizations_by_user
from open_schools_platform.student_management.student.selectors import get_student, get_student_profile


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
        circle = create_circle(name=create_circle_serializer.validated_data['name'], organization=organization)
        return Response(CircleSerializer(circle).data, status=201)


class CircleListApi(ApiAuthMixin, ListAPIView):

    def get_organization_circles(self, request, organization):
        serializer_class = CircleSerializer
        if not get_organization(filters={'id': str(organization)}):
            raise NotFound('There is no such organization')
        circles = get_circles(filters={'organization': str(organization)}, user=request.user)
        if not circles:
            raise NotFound('There are no circles in this organization')
        serializer = serializer_class(circles, many=True)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Get all circles for provided student profile",
        tags=[SwaggerTags.ORGANIZATION_MANAGEMENT_CIRCLES],
        manual_parameters=[
            Parameter('organization', IN_QUERY, required=False, type=TYPE_STRING),  # type: ignore
            Parameter('student_profile', IN_QUERY, required=False, type=TYPE_STRING),  # type: ignore
        ],
    )
    def get(self, request):
        response = []
        if self.request.query_params.get('organization'):
            response = self.get_organization_circles(organization=self.request.query_params.get('organization'),
                                                     request=request)
        return response
