import uuid

from rest_framework import serializers

from open_schools_platform.query_management.queries.models import Query


class CreateQuerySerializer(serializers.ModelSerializer):
    recipient_ct = serializers.CharField(source="recipient_ct.name")
    sender_ct = serializers.CharField(source="sender_ct.name")
    body_ct = serializers.CharField(source="body_ct.name")

    class Meta:
        model = Query
        fields = ("recipient_id", "sender_id", "body_id", "recipient_ct", "sender_ct", "body_ct")


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.CharField(max_length=200)
