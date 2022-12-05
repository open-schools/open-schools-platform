from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.parent_management.families.models import Family


class FamilyHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_FAMILY_FIELDS)(read_only=True)

    class Meta:
        model = Family
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_FAMILY_FIELDS,
                                                               object_title='FamilyHistory',
                                                               model=Family).generate_schemas()
