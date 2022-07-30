from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import ApiListPagination, get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.parent_management.families.selectors import get_family, get_families
from open_schools_platform.parent_management.families.serializers import FamilyCreateSerializer, FamilySerializer
from open_schools_platform.parent_management.families.services import create_family
from rest_framework.response import Response

from open_schools_platform.student_management.students.serializers import StudentProfileSerializer


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
        return Response({"family": FamilySerializer(family).data}, status=201)


class FamilyStudentProfilesListApi(ApiAuthMixin, APIView):
    pagination_class = ApiListPagination
    serializer_class = StudentProfileSerializer

    @swagger_auto_schema(
        operation_description="Get all student profiles for provided family.",
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request, pk):
        family = get_family(filters={'id': str(pk)}, user=request.user)
        if not family:
            raise NotFound("There is no such family")

        response = get_paginated_response(
            pagination_class=ApiListPagination,
            serializer_class=StudentProfileSerializer,
            queryset=family.student_profiles.all(),
            request=request,
            view=self,
        )
        return response


class FamiliesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all families for currently logged in user",
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request):
        families = get_families(filters={"parent_profiles": str(request.user.parent_profile.id)})
        if not families:
            raise NotFound("User has no families")
        return Response({"results": FamilySerializer(families, many=True).data}, status=200)
