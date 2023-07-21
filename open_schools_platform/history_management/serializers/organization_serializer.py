from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.organization_management.organizations.models import Organization


class GetOrganizationHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'inn', 'history_id', 'history_user_id', 'history_date', 'history_type')
