import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.employees.serializers import QueryEmployeeSerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.serializers import QueryStudentSerializer


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.CharField(max_length=200)


class OrganizationQuerySerializer(serializers.ModelSerializer):
    body = QueryEmployeeSerializer()

    class Meta:
        model = Query
        fields = ('id', 'sender_ct', 'sender_id', 'recipient_ct', 'recipient_id', 'status', 'body')


class StudentProfileQuerySerializer(serializers.ModelSerializer):
    body = QueryStudentSerializer()

    class Meta:
        model = Query
        fields = ('id', 'sender_ct', 'sender_id', 'recipient_ct', 'recipient_id', 'status', 'body')
