# Create your tests here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.parent_management.families.services import \
    get_families_that_interact_with_organization
from open_schools_platform.ticket_management.tickets.filters import TicketCommentFilter
from open_schools_platform.ticket_management.tickets.models import TicketComment, Ticket
from open_schools_platform.ticket_management.tickets.paginators import ApiTicketCommentsListPagination
from open_schools_platform.ticket_management.tickets.selectors import get_ticket, get_comments, get_comment
from open_schools_platform.ticket_management.tickets.serializers import GetTicketCommentSerializer, \
    CreateTicketCommentSerializer, CreateFamilyOrganizationTicketSerializer, \
    GetFamilyOrganizationTicketSerializer, UpdateTicketCommentSerializer
from open_schools_platform.ticket_management.tickets.services import create_ticket_comment, \
    create_family_organization_ticket, update_ticket_comment
from rest_framework.response import Response


class TicketCommentListApi(ApiAuthMixin, ListAPIView):
    queryset = TicketComment.objects.all()
    filterset_class = TicketCommentFilter
    pagination_class = ApiTicketCommentsListPagination
    serializer_class = GetTicketCommentSerializer

    @swagger_auto_schema(
        operation_description="Get all ticket comments of provided ticket.",
        tags=[SwaggerTags.TICKET_MANAGEMENT_TICKET]
    )
    def get(self, request, ticket_id):
        ticket = get_ticket(
            filters={'id': str(ticket_id)},
            user=request.user,
            empty_exception=True,
        )
        ticket_comments = get_comments(
            filters={'ticket': ticket},
        )

        response = get_paginated_response(
            pagination_class=ApiTicketCommentsListPagination,
            serializer_class=GetTicketCommentSerializer,
            queryset=ticket_comments,
            request=request,
            view=self
        )
        return response


class TicketCommentCreateApi(ApiAuthMixin, CreateAPIView):
    queryset = TicketComment.objects.all()
    pagination_class = ApiTicketCommentsListPagination
    serializer_class = CreateTicketCommentSerializer

    @swagger_auto_schema(
        operation_description="Create a new comment for provided ticket.",
        responses={201: convert_dict_to_serializer({"ticket_comment": GetTicketCommentSerializer()})},
        tags=[SwaggerTags.TICKET_MANAGEMENT_TICKET]
    )
    def post(self, request, ticket_id):
        create_ticket_comment_serializer = CreateTicketCommentSerializer(data=request.data)
        create_ticket_comment_serializer.is_valid(raise_exception=True)
        ticket = get_ticket(
            filters={'id': str(ticket_id)},
            user=request.user,
            empty_exception=True,
        )

        ticket_comment = create_ticket_comment(
            ticket=ticket,
            user=request.user,
            **create_ticket_comment_serializer.validated_data
        )
        return Response(
            {"ticket_comment": GetTicketCommentSerializer(ticket_comment, context={'request': request}).data},
            status=201)


class TicketCreateApi(ApiAuthMixin, CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = CreateFamilyOrganizationTicketSerializer

    @swagger_auto_schema(
        operation_description="Create a ticket for provided organization and user parent profile with first message.",
        responses={201: convert_dict_to_serializer({"ticket_comment": GetFamilyOrganizationTicketSerializer()})},
        tags=[SwaggerTags.TICKET_MANAGEMENT_TICKET]
    )
    def post(self, request):
        create_ticket_serializer = CreateFamilyOrganizationTicketSerializer(data=request.data)
        create_ticket_serializer.is_valid(raise_exception=True)

        organization = get_organization(
            filters={"id": create_ticket_serializer.validated_data['organization']},
            empty_exception=True,
        )

        families = get_families_that_interact_with_organization(request.user, organization)

        if len(families) == 0:
            raise PermissionDenied(
                "This organization is not related to user families. "
                "Your user families should be connected at least with one circle of provided organization.")

        ticket = create_family_organization_ticket(
            family=families[0],
            organization=organization
        )

        create_ticket_comment(ticket=ticket, user=request.user,
                              **create_ticket_serializer.validated_data['first_message'])

        return Response(
            {"ticket": GetFamilyOrganizationTicketSerializer(ticket, context={'request': request}).data},
            status=201)


class TicketCommentUpdateApi(ApiAuthMixin, APIView):

    @swagger_auto_schema(
        operation_description="Update ticket comment",
        tags=[SwaggerTags.TICKET_MANAGEMENT_TICKET],
        request_body=UpdateTicketCommentSerializer(),
        responses={200: convert_dict_to_serializer({"query": GetTicketCommentSerializer()}),
                   404: "No such ticket comment"}
    )
    def patch(self, request, ticket_comment_id):
        ticket_comment_update_serializer = UpdateTicketCommentSerializer(data=request.data)
        ticket_comment_update_serializer.is_valid(raise_exception=True)

        ticket_comment = get_comment(
            filters={'id': str(ticket_comment_id)},
            user=request.user,
            empty_exception=True,
        )
        ticket_comment = update_ticket_comment(ticket_comment=ticket_comment,
                                               data=ticket_comment_update_serializer.validated_data,
                                               user=request.user)
        return Response(
            {"ticket_comment": GetTicketCommentSerializer(ticket_comment, context={'request': request}).data},
            status=200)
