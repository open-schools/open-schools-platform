import uuid

from rest_framework import serializers

from open_schools_platform.query_management.queries.models import Query


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.CharField(max_length=200)


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'sender_ct', 'sender_id', 'recipient_ct', 'recipient_id', 'status')
