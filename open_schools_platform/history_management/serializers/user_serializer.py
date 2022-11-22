from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import get_history_records_field
from open_schools_platform.user_management.users.models import User


class UserHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", "id",
                                                "phone", "name", "last_login", "last_login_ip_address"))(read_only=True)

    class Meta:
        model = User
        fields = ('history',)
