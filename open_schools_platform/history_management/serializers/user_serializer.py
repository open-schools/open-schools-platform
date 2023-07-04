from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.user_management.users.models import User


class UserHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    last_login = serializers.CharField(required=False)
    last_login_ip_address = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'phone', 'last_login', 'last_login_ip_address', 'history_id', 'history_user_id',
            'history_date',
            'history_type')
