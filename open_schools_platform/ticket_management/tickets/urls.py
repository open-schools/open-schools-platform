from django.urls import path

from open_schools_platform.ticket_management.tickets.views import TicketCommentListApi, TicketCommentCreateApi, \
    TicketCreateApi, TicketCommentUpdateApi

urlpatterns = [
    path('/<uuid:ticket_id>/comments', TicketCommentListApi.as_view(), name='ticket-comments'),
    path('/<uuid:ticket_id>/comment', TicketCommentCreateApi.as_view(), name='create-ticket-comment'),
    path('', TicketCreateApi.as_view(), name='create-ticket'),
    path('/ticket-comment/<uuid:ticket_comment_id>', TicketCommentUpdateApi.as_view(), name='update-ticket-comment'),
]
