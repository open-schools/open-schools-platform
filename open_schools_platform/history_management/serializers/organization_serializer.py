from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(
        fields=HistoryFields().HISTORY_ORGANIZATION_FIELDS)(read_only=True)

    class Meta:
        model = Organization
        fields = ("history",)
