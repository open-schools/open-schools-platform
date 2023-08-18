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
    parent_phones = serializers.SerializerMethodField('get_parent_phones')

    def get_parent_phones(self, obj):
        return ",".join(map(lambda x: str(x.user.phone), obj.parent_profiles.all()))

    class Meta:
        model = Family
        fields = ("id", "name", "parent_phones")


class CreateFamilyInviteParentSerializer(serializers.Serializer):
    family = serializers.UUIDField(required=True)
    phone = PhoneNumberField(required=True, max_length=17)
