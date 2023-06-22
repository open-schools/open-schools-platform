import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.circles.serializers import QueryCircleRecipientSerializer
from open_schools_platform.organization_management.employees.serializers import QueryEmployeeBodySerializer, \
    EmployeeProfileSerializer
from open_schools_platform.organization_management.organizations.serializers import OrganizationSerializer
from open_schools_platform.parent_management.families.serializers import FamilySerializer
from open_schools_platform.parent_management.parents.serializers import QueryParentProfileRecipientSerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.serializers import StudentProfileAdditionalSerializer, \
    StudentProfileSerializer, StudentSerializer


class QueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.ChoiceField(choices=Query.Status.choices)


class QuerySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.Status.choices)

    class Meta:
        model = Query
        fields = ('id', 'sender', 'recipient', 'status', 'body', 'additional')


class EmployeeProfileQuerySerializer(QuerySerializer):
    sender = OrganizationSerializer()
    recipient = EmployeeProfileSerializer()
    body = QueryEmployeeBodySerializer()


class StudentProfileQuerySerializer(QuerySerializer):
    sender = StudentProfileSerializer.with_fields(['id', 'photo'])()
    recipient = QueryCircleRecipientSerializer()
    body = StudentSerializer.with_fields(['id', 'name'])()
    additional = StudentProfileAdditionalSerializer()


class InviteParentQuerySerializer(QuerySerializer):
    sender = FamilySerializer()
    recipient = QueryParentProfileRecipientSerializer()
