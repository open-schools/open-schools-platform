from rest_framework import serializers

from open_schools_platform.organization_management.circles.models import Circle


class CreateCircleSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(required=True)

    class Meta:
        model = Circle
        fields = ('name', 'organization', 'address', 'capacity', 'description')
        extra_kwargs = {'address': {'required': True},
                        'capacity': {'required': True},
                        'description': {'required': True}}


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', 'organization', 'address', 'capacity', 'description', 'latitude', 'longitude')


class QueryCircleRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', )
