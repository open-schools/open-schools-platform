import uuid

from rest_framework import serializers


class FamilySerializer(serializers.Serializer):
    parent_profile = serializers.UUIDField(default=uuid.uuid4)
    name = serializers.CharField(default=None, required=False, max_length=200)
