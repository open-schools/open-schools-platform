import uuid

from django.core.validators import MinValueValidator
from rest_framework import serializers


class StudentProfileSerializer(serializers.Serializer):
    age = serializers.IntegerField(validators=[MinValueValidator(0)])
    name = serializers.CharField(max_length=200)
    family = serializers.UUIDField(default=uuid.uuid4)
