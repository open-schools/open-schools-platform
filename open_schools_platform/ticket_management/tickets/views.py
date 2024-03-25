# Create your tests here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.ticket_management.tickets.filters import TicketCommentFilter
from open_schools_platform.ticket_management.tickets.models import TicketComment
from open_schools_platform.ticket_management.tickets.paginators import ApiTicketCommentsListPagination
from open_schools_platform.ticket_management.tickets.selectors import get_ticket, get_comments
from open_schools_platform.ticket_management.tickets.serializers import GetTicketCommentSerializer


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
