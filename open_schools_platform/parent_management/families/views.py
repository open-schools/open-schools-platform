from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.constants import NotificationType
from open_schools_platform.errors.exceptions import AlreadyExists
from open_schools_platform.parent_management.families.constants import FamilyConstants
from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.paginators import ApiFamiliesListPagination
from open_schools_platform.student_management.students.filters import StudentProfileFilter
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.student_management.students.paginators import ApiStudentProfilesListPagination
from open_schools_platform.student_management.students.selectors import get_student_profiles_from_family_with_filters
from open_schools_platform.user_management.users.services import notify_user
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.parent_management.families.selectors import get_family, get_families
from open_schools_platform.parent_management.families.serializers import CreateFamilySerializer, GetFamilySerializer, \
    CreateFamilyInviteParentSerializer
from open_schools_platform.parent_management.families.services import create_family
from rest_framework.response import Response

from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.query_management.queries.serializers import GetQueryStatusSerializer
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.serializers import GetStudentProfileSerializer


class FamilyApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Creates Family.\n"
                              "Returns Family data.",
        request_body=CreateFamilySerializer,
        responses={201: convert_dict_to_serializer({"family": GetFamilySerializer()})},
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def post(self, request):
        family_create_serializer = CreateFamilySerializer(data=request.data)
        family_create_serializer.is_valid(raise_exception=True)
        family = create_family(name=family_create_serializer.validated_data["name"], parent=request.user.parent_profile)
        return Response({"family": GetFamilySerializer(family).data}, status=201)


class FamilyStudentProfilesListApi(ApiAuthMixin, ListAPIView):
    queryset = StudentProfile.objects.all()
    filterset_class = StudentProfileFilter
    pagination_class = ApiStudentProfilesListPagination
    serializer_class = GetStudentProfileSerializer

    @swagger_auto_schema(
        operation_description="Get all student profiles for provided family.",
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request, family_id):
        family = get_family(
            filters={'id': str(family_id)},
            user=request.user,
            empty_exception=True,
        )
        response = get_paginated_response(
            pagination_class=ApiStudentProfilesListPagination,
            serializer_class=GetStudentProfileSerializer,
            queryset=get_student_profiles_from_family_with_filters(family, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class FamiliesListApi(ApiAuthMixin, ListAPIView):
    queryset = Family.objects.all()
    filterset_class = FamilyFilter
    pagination_class = ApiFamiliesListPagination
    serializer_class = GetFamilySerializer

    @swagger_auto_schema(
        operation_description="Get all families for currently logged in user",
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES]
    )
    def get(self, request):
        families = get_families(
            filters=request.GET.dict() | {"parent_profiles": str(request.user.parent_profile.id)}
        )
        response = get_paginated_response(
            pagination_class=ApiFamiliesListPagination,
            serializer_class=GetFamilySerializer,
            queryset=families,
            request=request,
            view=self
        )
        return response


class InviteParentApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES],
        request_body=CreateFamilyInviteParentSerializer,
        responses={201: convert_dict_to_serializer({"query": GetQueryStatusSerializer()}),
                   400: "Parent is already in this family",
                   404: "No such family"},
        operation_description="Creates invite parent query.",
    )
    def post(self, request):
        invite_parent_serializer = CreateFamilyInviteParentSerializer(data=request.data)
        invite_parent_serializer.is_valid(raise_exception=True)
        family = get_family(filters={"id": str(invite_parent_serializer.validated_data["family"])}, user=request.user,
                            empty_exception=True)
        parent = get_parent_profile(filters={"phone": str(invite_parent_serializer.validated_data["phone"])},
                                    empty_exception=True,
                                    empty_message="There is no parent_profile with such phone")
        if parent in family.parent_profiles.all():
            raise AlreadyExists("Parent is already in this family")
        query = create_query(sender_model_name="family", sender_id=family.id,
                             recipient_model_name="parentprofile", recipient_id=parent.id)
        notify_user(user=parent.user, title=FamilyConstants.INVITE_PARENT_TITLE,
                    body=FamilyConstants.get_invite_parent_message(family),
                    data={"query": str(query.id), "type": NotificationType.InviteParent})
        return Response({"query": GetQueryStatusSerializer(query).data}, status=201)


class FamilyDeleteApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_FAMILIES],
        operation_description="Delete family.",
        responses={204: "Successfully deleted", 404: "No such family"}
    )
    def delete(self, request, family_id):
        family = get_family(filters={'id': family_id}, empty_exception=True, user=request.user)
        family.delete()
        return Response(status=204)
