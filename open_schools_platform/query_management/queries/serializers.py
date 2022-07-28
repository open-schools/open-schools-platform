import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.employees.serializers import QueryEmployeeBodySerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.serializers import QueryStudentBodySerializer


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.CharField(max_length=200)


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'sender_id', 'recipient_id', 'status', 'body')


class OrganizationQuerySerializer(QuerySerializer):
    body = QueryEmployeeBodySerializer()


class EmployeeProfileQuerySerializer(QuerySerializer):
    body = QueryEmployeeBodySerializer()


class StudentProfileQuerySerializer(QuerySerializer):
    body = QueryStudentBodySerializer()
