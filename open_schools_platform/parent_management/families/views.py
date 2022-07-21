from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.parent_management.families.serializers import FamilyCreateSerializer, FamilySerializer
from open_schools_platform.parent_management.families.services import create_family
from rest_framework.response import Response


class FamilyApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Family.\n"
                              "Returns Family data.",
        request_body=FamilyCreateSerializer,
        responses={201: FamilySerializer},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def post(self, request):
        family_create_serializer = FamilyCreateSerializer(data=request.data)
        family_create_serializer.is_valid(raise_exception=True)
        family = create_family(name=family_create_serializer.validated_data["name"], parent=request.user.parent_profile)
        return Response(FamilySerializer(family).data, status=201)
