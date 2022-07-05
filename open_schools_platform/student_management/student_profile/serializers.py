import uuid

from rest_framework import serializers


class StudentProfileSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    family = serializers.UUIDField(default=uuid.uuid4)
