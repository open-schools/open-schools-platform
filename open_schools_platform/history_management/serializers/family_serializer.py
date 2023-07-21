from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.parent_management.families.models import Family


class GetFamilyHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Family
        fields = ('id', 'name', 'history_id', 'history_user_id', 'history_date', 'history_type')
