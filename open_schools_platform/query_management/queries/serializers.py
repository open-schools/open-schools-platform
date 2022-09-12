import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.circles.serializers import QueryCircleRecipientSerializer
from open_schools_platform.organization_management.employees.serializers import QueryEmployeeBodySerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.serializers import QueryStudentBodySerializer, \
    QueryStudentProfileAdditionalSerializer, QueryStudentProfileSenderSerializer


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.ChoiceField(choices=Query.Status.choices)


class QuerySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.Status.choices)

    class Meta:
        model = Query
        fields = ('id', 'sender', 'recipient', 'status', 'body', 'additional')


class EmployeeProfileQuerySerializer(QuerySerializer):
    body = QueryEmployeeBodySerializer()


class StudentProfileQuerySerializer(QuerySerializer):
    sender = QueryStudentProfileSenderSerializer()
    recipient = QueryCircleRecipientSerializer()
    body = QueryStudentBodySerializer()
    additional = QueryStudentProfileAdditionalSerializer()
