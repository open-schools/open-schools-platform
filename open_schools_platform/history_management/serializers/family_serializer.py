from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.parent_management.families.models import Family


class FamilyHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(
        fields=HistoryFields().HISTORY_FAMILY_FIELDS)(read_only=True)

    class Meta:
        model = Family
        fields = ("history",)
