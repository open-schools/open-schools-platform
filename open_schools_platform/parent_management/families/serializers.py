from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.parent_management.families.models import Family


class CreateFamilySerializer(serializers.Serializer):
    name = serializers.CharField(default=None, required=False, max_length=200)


class GetFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ("id", "name")


class GetFamilySenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ("id", "name")


class GetFamilyRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ("id", "name")


class CreateFamilyInviteParentSerializer(serializers.Serializer):
    family = serializers.UUIDField(required=True)
    phone = PhoneNumberField(required=True, max_length=17)
