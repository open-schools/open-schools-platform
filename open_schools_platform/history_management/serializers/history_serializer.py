from rest_framework import serializers


class BaseHistorySerializer(serializers.Serializer):
    history_id = serializers.IntegerField()
    history_user_id = serializers.UUIDField()
    history_date = serializers.DateTimeField()
    history_type = serializers.CharField()
