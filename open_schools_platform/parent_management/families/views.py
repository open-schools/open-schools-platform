from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotAcceptable
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.firebase.utils import notify_user
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.parent_management.families.selectors import get_family, get_families
from open_schools_platform.parent_management.families.serializers import FamilyCreateSerializer, FamilySerializer, \
    FamilyInviteParentSerializer
from open_schools_platform.parent_management.families.services import create_family
from rest_framework.response import Response

from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.query_management.queries.serializers import QueryStatusSerializer
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.serializers import StudentProfileSerializer


class FamilyApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Family.\n"
                              "Returns Family data.",
        request_body=FamilyCreateSerializer,
        responses={201: swagger_dict_response({"family": FamilySerializer()})},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def post(self, request):
        family_create_serializer = FamilyCreateSerializer(data=request.data)
        family_create_serializer.is_valid(raise_exception=True)
        family = create_family(name=family_create_serializer.validated_data["name"], parent=request.user.parent_profile)
        return Response({"family": FamilySerializer(family).data}, status=201)


class FamilyStudentProfilesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all student profiles for provided family.",
        responses={200: swagger_dict_response({"results": StudentProfileSerializer(many=True)})},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request, pk):
        family = get_family(
            filters={'id': str(pk)},
            user=request.user,
            empty_exception=True,
            empty_message="There is no such family",
        )
        return Response({"results": StudentProfileSerializer(family.student_profiles, many=True).data}, status=200)


class FamiliesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get all families for currently logged in user",
        responses={200: swagger_dict_response({"results": FamilySerializer(many=True)})},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request):
        families = get_families(
            filters={"parent_profiles": str(request.user.parent_profile.id)},
            empty_exception=True,
            empty_message="There is no such family",
        )
        return Response({"results": FamilySerializer(families, many=True).data}, status=200)


class InviteParentApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES],
        request_body=FamilyInviteParentSerializer,
        responses={201: swagger_dict_response({"query": QueryStatusSerializer()}),
                   404: "There is no such family",
                   406: "Parent is already in this family"},
        operation_description="Creates invite parent query.",
    )
    def post(self, request):
        invite_parent_serializer = FamilyInviteParentSerializer(data=request.data)
        invite_parent_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": str(invite_parent_serializer.validated_data["family"])}, user=request.user,
                            empty_exception=True, empty_message="There is no such family")
        parent = get_parent_profile(filters={"phone": str(invite_parent_serializer.validated_data["phone"])},
                                    empty_exception=True,
                                    empty_message="There is no parent_profile with such phone")
        if parent in family.parent_profiles.all():
            raise NotAcceptable("Parent is already in this family")
        query = create_query(sender_model_name="family", sender_id=family.id,
                             recipient_model_name="parentprofile", recipient_id=parent.id)
        notify_user(user=parent.user, title='Вы были приглашены в семью!',
                    body=f'семья {family.name} пригласила вас к себе!')
        return Response({"query": QueryStatusSerializer(query).data}, status=201)
