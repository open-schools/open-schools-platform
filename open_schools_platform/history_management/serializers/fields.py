from rest_framework import serializers


class HistorySerializerFields:
    HISTORY_USER_FIELDS = ["id", "name", "phone", "last_login", "last_login_ip_address"]
    HISTORY_FAMILY_FIELDS = ["id", "name"]
    HISTORY_CIRCLE_FIELDS = ['id', 'name', 'organization', 'address', 'capacity', 'description']
    HISTORY_EMPLOYEE_FIELDS = ["id", "name", "organization", "position"]
    HISTORY_EMPLOYEE_PROFILE_FIELDS = ["id", "name", "user"]
    HISTORY_ORGANIZATION_FIELDS = ["id", "name", "inn"]
    HISTORY_PARENT_PROFILES_FIELDS = ["id", "name", "user"]
    HISTORY_STUDENT_FIELDS = ["id", "name", "circle", "student_profile"]
    HISTORY_STUDENT_PROFILES_FIELDS = ["id", "name", "phone", "age", "photo"]

    @staticmethod
    def get_history_records_field(fields: list):
        class HistoryRecordsField(serializers.ListField):
            child = serializers.DictField()

            def to_representation(self, data):
                return super().to_representation(
                    data.values(*fields))

        return HistoryRecordsField

    def __getattribute__(self, item):
        return ["history_id", "history_user_id", "history_date", "history_type"] + object.__getattribute__(self, item)
