from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.parent_management.parents.models import ParentProfile


class GetParentProfileHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = ParentProfile
        fields = ('id', 'name', 'user', 'history_id', 'history_user_id', 'history_date', 'history_type')
