from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import get_history_records_field
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", "id",
                                                "name", "inn",))(read_only=True)

    class Meta:
        model = Organization
        fields = ("history",)
