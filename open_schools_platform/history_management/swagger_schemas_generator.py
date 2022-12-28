from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info

from open_schools_platform.history_management.serializers.fields import HISTORY_BASE_FIELDS


class SwaggerSchemasHistoryGenerator:
    def __init__(self, fields: list, object_title: str, model):
        self.fields = fields
        self.object_title = object_title
        self.model = model

    def _get_field_type_info(self, field_name) -> dict:
        model_field = self.model._meta.get_field(field_name)
        field = get_basic_type_info(model_field)
        if not field:
            return {"type": openapi.TYPE_STRING, "title": str(model_field)}
        return field

    def _properties_dict_generator(self):
        for field in self.fields:
            if field not in HISTORY_BASE_FIELDS:
                info = self._get_field_type_info(field_name=field)
                yield {field: openapi.Schema(**info)}
            else:
                yield {field: openapi.Schema(type=openapi.TYPE_STRING)}

    def _get_properties_dict(self):
        properties = dict()
        for property_dict in self._properties_dict_generator():
            properties |= property_dict
        return properties

    def generate_schemas(self) -> dict:
        schema = {
            "type": openapi.TYPE_OBJECT,
            "title": self.object_title,
            "properties": self._get_properties_dict(),
        }
        return schema
