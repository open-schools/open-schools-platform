from rest_framework import serializers

from open_schools_platform.common.serializers import BaseModelSerializer
from open_schools_platform.common.validators import only_true_value
from open_schools_platform.organization_management.organizations.serializers import GetOrganizationSerializer
from open_schools_platform.parent_management.families.serializers import GetFamilySerializer
from open_schools_platform.ticket_management.tickets.models import TicketComment, Ticket


class GetTicketCommentSenderSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class GetTicketCommentSerializer(BaseModelSerializer):
    sender = GetTicketCommentSenderSerializer()

    class Meta:
        model = TicketComment
        fields = ("id", "is_sender", "is_seen", "value", "created_at", "sender", "is_internal_recipient")


class CreateTicketCommentSerializer(BaseModelSerializer):
    sender_ct = serializers.CharField(required=False)

    class Meta:
        model = TicketComment
        fields = ("value", "is_sender", "sender_id", "sender_ct", "is_internal_recipient")


class GetFamilyOrganizationTicketSerializer(BaseModelSerializer):
    last_comment = GetTicketCommentSerializer()
    recipient = GetOrganizationSerializer()
    sender = GetFamilySerializer()

    class Meta:
        model = Ticket
        fields = ("id", "last_comment", "recipient", "sender", "created_at", "unread_sender_comments_count",
                  "unread_recipient_comments_count", "status")


class CreateFamilyOrganizationTicketSerializer(BaseModelSerializer):
    organization = serializers.UUIDField(required=True)
    first_message = CreateTicketCommentSerializer(required=True)

    class Meta:
        model = Ticket
        fields = ('organization', 'first_message')


class UpdateTicketCommentSerializer(BaseModelSerializer):
    is_seen = serializers.BooleanField(validators=[only_true_value])

    class Meta:
        model = TicketComment
        fields = ('is_seen',)
