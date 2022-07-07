import uuid

from django.core.validators import MinValueValidator
from rest_framework import serializers


class StudentProfileSerializer(serializers.Serializer):
    age = serializers.IntegerField(validators=[MinValueValidator(0)])
    name = serializers.CharField(max_length=200)
    family = serializers.UUIDField(default=uuid.uuid4)


class StudentProfileUpdateSerializer(serializers.Serializer):
    student_profile = serializers.UUIDField(default=uuid.uuid4)
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)
