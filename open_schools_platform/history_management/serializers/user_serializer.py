from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.user_management.users.models import User


class UserHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_USER_FIELDS)(read_only=True)

    class Meta:
        model = User
        fields = ('history',)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_USER_FIELDS,
                                                               object_title='UserHistory').generate_schemas()
