import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.circles.models import Circle


class CreateCircleSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(default=uuid.uuid4)

    class Meta:
        model = Circle
        fields = ('name', 'organization', 'address', 'capacity', 'description', 'latitude', 'longitude')


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', 'organization', 'address', 'capacity', 'description', 'latitude', 'longitude')
