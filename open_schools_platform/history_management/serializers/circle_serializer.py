from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.organization_management.circles.models import Circle


class CircleHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_CIRCLE_FIELDS)(read_only=True)

    class Meta:
        model = Circle
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_CIRCLE_FIELDS,
                                                               object_title='CircleHistory').generate_schemas()
