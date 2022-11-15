from rest_framework import serializers

from open_schools_platform.user_management.users.models import User


class HistoryRecordsField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values("history_id", "history_user_id", "history_date", "history_type",
                                                     "id", "phone", "name", "last_login", "last_login_ip_address"))


class UserHistorySerializer(serializers.ModelSerializer):
    history = HistoryRecordsField(read_only=True)

    class Meta:
        model = User
        fields = ("history",)
