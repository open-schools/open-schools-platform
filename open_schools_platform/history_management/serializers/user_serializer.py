from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.user_management.users.models import User


class UserHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(fields=HistoryFields().HISTORY_USER_FIELDS)(read_only=True)

    class Meta:
        model = User
        fields = ('history',)
