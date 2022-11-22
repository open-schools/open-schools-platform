from rest_framework import serializers


def get_history_records_field(fields: tuple):
    class HistoryRecordsField(serializers.ListField):
        child = serializers.DictField()

        def to_representation(self, data):
            return super().to_representation(
                data.values(*fields))
    return HistoryRecordsField
