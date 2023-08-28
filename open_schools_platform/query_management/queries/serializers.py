import uuid

from rest_framework import serializers

from open_schools_platform.organization_management.circles.serializers import GetCircleRecipientSerializer, \
    GetCircleSenderSerializer
from open_schools_platform.organization_management.employees.serializers import GetEmployeeBodySerializer, \
    GetEmployeeProfileRecipientSerializer
from open_schools_platform.organization_management.organizations.serializers import GetOrganizationSenderSerializer
from open_schools_platform.parent_management.families.serializers import GetFamilySenderSerializer, \
    GetFamilyRecipientSerializer
from open_schools_platform.parent_management.parents.serializers import ParentProfileRecipientSerializer
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.serializers import GetStudentJoinCircleContext, \
    GetStudentProfileSenderForOrganizationSerializer, GetStudentBodySerializer, GetCircleInviteStudentContext


class GetQueryStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4())
    status = serializers.ChoiceField(choices=Query.Status.choices)


class QuerySerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Query.Status.choices)

    class Meta:
        model = Query
        fields = ('id', 'sender', 'recipient', 'status', 'body', 'additional')


class GetOrganizationInviteEmployeeSerializer(QuerySerializer):
    sender = GetOrganizationSenderSerializer()
    recipient = GetEmployeeProfileRecipientSerializer()
    body = GetEmployeeBodySerializer()


class GetCircleInviteStudentSerializer(QuerySerializer):
    sender = GetCircleSenderSerializer()
    recipient = GetFamilyRecipientSerializer()
    body = GetStudentBodySerializer()
    additional = GetCircleInviteStudentContext()


class GetStudentJoinCircleSerializer(QuerySerializer):
    sender = GetStudentProfileSenderForOrganizationSerializer()
    recipient = GetCircleRecipientSerializer()
    body = GetStudentBodySerializer()
    additional = GetStudentJoinCircleContext()


class GetFamilyInviteParentSerializer(QuerySerializer):
    sender = GetFamilySenderSerializer()
    recipient = ParentProfileRecipientSerializer()
