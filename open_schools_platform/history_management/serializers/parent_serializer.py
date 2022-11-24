from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import get_history_records_field
from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", 'id',
                                                'name', 'user'))(read_only=True)

    class Meta:
        model = ParentProfile
        fields = ("history",)
