from open_schools_platform.common.serializers import BaseModelSerializer
from open_schools_platform.ticket_management.tickets.models import TicketComment


class GetTicketCommentSerializer(BaseModelSerializer):

    class Meta:
        model = TicketComment
        fields = ("id", "is_sender", "is_seen", "value", "created_at")


class CreateTicketCommentSerializer(BaseModelSerializer):

    class Meta:
        model = TicketComment
        fields = ("value", )
