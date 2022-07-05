from django.contrib.auth import get_user
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import CreateAPIView

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.parent_management.families.serializers import FamilySerializer
from open_schools_platform.parent_management.families.services import create_family, add_parents_to_family, \
    generate_name_for_family
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from rest_framework.response import Response


class FamilyApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Creates Family via provided parent id and name\n"
                              "Returns Family data.",
        request_body=FamilySerializer,
        responses={201: "Family was successfully created", 404: "There is no such parent",
                   403: "User is not logged in"},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def post(self, request):
        family_serializer = FamilySerializer(data=request.data)
        family_serializer.is_valid(raise_exception=True)
        user = get_user(request)
        parent = get_parent_profile(filters={"id": family_serializer.validated_data['parent_profile']})
        if not parent:
            raise NotFound('There is no such parent')
        if parent.user != user:
            raise PermissionDenied
        family_name = generate_name_for_family(parent=parent, family_name=family_serializer.validated_data['name'])
        family = create_family(name=family_name)
        add_parents_to_family(family=family, parent=parent)
        return Response({"family_id": family.id, "family_name": family_name,
                         "family_parent": family_serializer.validated_data['parent_profile']}, status=201)
