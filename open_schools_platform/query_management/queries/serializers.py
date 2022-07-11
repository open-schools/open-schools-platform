import uuid

from rest_framework import serializers


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.CharField(max_length=200)
