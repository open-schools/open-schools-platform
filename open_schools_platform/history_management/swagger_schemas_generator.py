from drf_yasg import openapi


class SwaggerSchemasHistoryGenerator:
    def __init__(self, fields: list, object_title: str):
        self.fields = fields
        self.object_title = object_title

    def generate_schemas(self):
        result = {
            "type": openapi.TYPE_OBJECT,
            "title": self.object_title,
            "properties": {field: openapi.Schema(type=openapi.TYPE_STRING,) for field in self.fields}
        }
        return result
