from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.common.views import convert_dict_to_serializer
from rest_framework.response import Response

from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.paginators import OrganizationApiListPagination
from open_schools_platform.organization_management.organizations.serializers import GetOrganizationSerializer
from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.parent_management.families.services import get_accessible_organizations
from open_schools_platform.parent_management.parents.services import get_last_organization_tickets
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.query_management.queries.serializers import GetFamilyInviteParentSerializer, \
    GetStudentJoinCircleSerializer
from open_schools_platform.student_management.students.selectors import get_student_profiles_by_families
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from open_schools_platform.ticket_management.tickets.paginators import ApiTicketListPagination
from open_schools_platform.ticket_management.tickets.selectors import get_tickets, get_comments
from open_schools_platform.ticket_management.tickets.serializers import GetFamilyOrganizationTicketSerializer, \
    GetTicketCommentSerializer


class InviteParentQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        responses={200: convert_dict_to_serializer({"results": GetFamilyInviteParentSerializer(many=True)}),
                   404: "There are no queries with such recipient"},
        operation_description="Get all invite-parent queries for parent_profile of current user",
    )
    def get(self, request):
        queries = get_queries(
            filters={'recipient_id': str(request.user.parent_profile.id)}
        )
        return Response({"results": GetFamilyInviteParentSerializer(queries, many=True).data}, status=200)


class GetAccessibleOrganizationListApi(ApiAuthMixin, ListAPIView):
    queryset = Organization.objects.all()
    filterset_class = OrganizationFilter
    pagination_class = OrganizationApiListPagination
    serializer_class = GetOrganizationSerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        operation_description="Get all organization which users can interact",
    )
    def get(self, request):
        response = get_paginated_response(
            pagination_class=OrganizationApiListPagination,
            serializer_class=GetOrganizationSerializer,
            queryset=get_accessible_organizations(request.user, request.GET.dict()),
            request=request,
            view=self
        )
        return response


class StudentJoinCircleQueriesListApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        responses={200: convert_dict_to_serializer({"results": GetStudentJoinCircleSerializer(many=True)})},
        operation_description="Get all student-join-circle queries that are accessible by current user's parent_profile"
    )
    def get(self, request):
        families = get_families(
            filters={"parent_profiles": str(request.user.parent_profile.id)},
        )
        student_profiles = get_student_profiles_by_families(families)
        queries = get_queries(filters={"sender_ids": form_ids_string_from_queryset(student_profiles)})
        return Response(
            {"results": GetStudentJoinCircleSerializer(queries, many=True, context={'request': request}).data},
            status=200)


class FamilyOrganizationTicketsListApi(ApiAuthMixin, ListAPIView):
    queryset = Ticket.objects.all()
    pagination_class = ApiTicketListPagination
    serializer_class = GetFamilyOrganizationTicketSerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        operation_description="Get all last tickets to organizations of current parent profile.",
    )
    def get(self, request):
        tickets = get_tickets(
            filters={'sender_ids': form_ids_string_from_queryset(request.user.parent_profile.families.all()),
                     'recipient_ct': ContentType.objects.get(model="organization")}
        )

        response = get_paginated_response(
            pagination_class=ApiTicketListPagination,
            serializer_class=GetFamilyOrganizationTicketSerializer,
            queryset=get_last_organization_tickets(tickets),
            request=request,
            view=self
        )
        return response


class FamilyOrganizationTicketCommentsListApi(ApiAuthMixin, ListAPIView):
    queryset = TicketComment.objects.all()
    pagination_class = ApiTicketListPagination
    serializer_class = GetTicketCommentSerializer

    @swagger_auto_schema(
        tags=[SwaggerTags.PARENT_MANAGEMENT_PARENTS],
        operation_description="Get all comments for ticket organization",
    )
    def get(self, request, organization_id):
        tickets = get_tickets(
            filters={'recipient_id': organization_id,
                     'sender_ids': form_ids_string_from_queryset(request.user.parent_profile.families.all())}
        )

        ticket_comments = get_comments(
            filters={'ticket_ids': form_ids_string_from_queryset(tickets)},
            empty_filters=True
        )

        response = get_paginated_response(
            pagination_class=ApiTicketListPagination,
            serializer_class=GetTicketCommentSerializer,
            queryset=ticket_comments,
            request=request,
            view=self
        )
        return response
