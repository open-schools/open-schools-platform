from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(fields=HistoryFields().HISTORY_PARENT_FIELDS)(read_only=True)

    class Meta:
        model = ParentProfile
        fields = ("history",)
