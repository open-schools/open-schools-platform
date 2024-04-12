from rest_framework import serializers

from open_schools_platform.common.serializers import BaseModelSerializer
from open_schools_platform.common.validators import only_true_value
from open_schools_platform.organization_management.organizations.serializers import GetOrganizationSerializer
from open_schools_platform.ticket_management.tickets.models import TicketComment, Ticket


class GetTicketCommentSerializer(BaseModelSerializer):
    class Meta:
        model = TicketComment
        fields = ("id", "is_sender", "is_seen", "value", "created_at")


class CreateTicketCommentSerializer(BaseModelSerializer):
    class Meta:
        model = TicketComment
        fields = ("value", "is_sender")


class GetFamilyOrganizationTicketSerializer(BaseModelSerializer):
    last_comment = GetTicketCommentSerializer()
    recipient = GetOrganizationSerializer()

    class Meta:
        model = Ticket
        fields = ("id", "last_comment", "recipient", "created_at", "unread_sender_comments_count",
                  "unread_recipient_comments_count")


class CreateFamilyOrganizationTicketSerializer(BaseModelSerializer):
    family = serializers.UUIDField(required=True)
    organization = serializers.UUIDField(required=True)
    first_message = CreateTicketCommentSerializer(required=True)

    class Meta:
        model = Ticket
        fields = ('family', 'organization', 'first_message')


class UpdateTicketCommentSerializer(BaseModelSerializer):
    is_seen = serializers.BooleanField(validators=[only_true_value])

    class Meta:
        model = TicketComment
        fields = ('is_seen', )
