from django.urls import path

from open_schools_platform.ticket_management.tickets.views import TicketCommentListApi

urlpatterns = [
    path('/<uuid:ticket_id>/comments', TicketCommentListApi.as_view(), name='ticket-comments'),
]
