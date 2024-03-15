from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.query_management.queries.models import Query


class GetQueryHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Query
        fields = (
            'id', 'recipient_ct', 'recipient_id', 'sender_ct', 'sender_id', 'body_ct', 'body_id', 'additional_ct',
            'additional_id', 'history_id', 'history_user_id', 'status', 'history_date', 'history_type')
