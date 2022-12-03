from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_PARENT_PROFILES_FIELDS)(read_only=True)

    class Meta:
        model = ParentProfile
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(
            fields=HistorySerializerFields().HISTORY_PARENT_PROFILES_FIELDS,
            object_title='ParentProfileHistory').generate_schemas()
