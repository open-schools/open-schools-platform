from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.organization_management.circles.models import Circle


class CircleHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(fields=HistoryFields().HISTORY_CIRCLE_FIELDS)(read_only=True)

    class Meta:
        model = Circle
        fields = ("history",)
