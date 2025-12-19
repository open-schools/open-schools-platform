# common/audit/serializers.py
from rest_framework import serializers
from .models import AuditLog, AuditEventType
from open_schools_platform.user_management.users.serializers import GetUserSerializer
from open_schools_platform.marketplace_management.serializers import AppSerializer
from open_schools_platform.organization_management.organizations.serializers import GetOrganizationSerializer


class GetAuditLogSerializer(serializers.ModelSerializer):
    user = GetUserSerializer(read_only=True)
    app = AppSerializer(read_only=True)
    organization = GetOrganizationSerializer(read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'event_type',
            'event_type_display',
            'user',
            'app',
            'organization',
            'description',
            'metadata',
            'ip_address',
            'user_agent',
            'created_at',
        ]
        read_only_fields = fields


class AuditLogFilterSerializer(serializers.Serializer):
    """Сериализатор для фильтрации логов"""
    event_type = serializers.ChoiceField(
        choices=AuditEventType.choices,
        required=False,
        help_text="Тип события"
    )
    user_id = serializers.UUIDField(required=False, help_text="ID пользователя")
    app_id = serializers.UUIDField(required=False, help_text="ID приложения")
    organization_id = serializers.UUIDField(required=False, help_text="ID организации")
    date_from = serializers.DateField(required=False, help_text="Дата начала периода")
    date_to = serializers.DateField(required=False, help_text="Дата конца периода")
    search = serializers.CharField(required=False, help_text="Поиск по описанию")

    class Meta:
        fields = ['event_type', 'user_id', 'app_id', 'organization_id', 'date_from', 'date_to', 'search']