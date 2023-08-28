from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.organization_management.circles.models import Circle


class GetCircleHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', 'organization', 'address', 'capacity', 'description', 'history_id', 'history_user_id',
                  'history_date', 'history_type')
