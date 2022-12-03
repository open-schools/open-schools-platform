from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_ORGANIZATION_FIELDS)(read_only=True)

    class Meta:
        model = Organization
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(
            fields=HistorySerializerFields().HISTORY_ORGANIZATION_FIELDS,
            object_title='OrganizationHistory').generate_schemas()
