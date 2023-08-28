from rest_framework import serializers

from open_schools_platform.organization_management.circles.models import Circle


class GetShallowCircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', 'address', 'capacity', 'description', 'latitude', 'longitude')
