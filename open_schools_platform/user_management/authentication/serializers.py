from phonenumber_field.phonenumber import PhoneNumber, to_python
from rest_framework import serializers

from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.compat import gettext_lazy as _
from open_schools_platform.user_management.users.selectors import get_user


class JSONWebTokenWithTwoResponses(JSONWebTokenSerializer):

    def validate(self, data):
        try:
            response = super().validate(data)
        except serializers.ValidationError:
            if not PhoneNumber.is_valid(to_python(data.get(self.username_field))):
                msg = _('Invalid phone.')
                raise serializers.ValidationError(msg)

            user = get_user(filters={"phone": data.get(self.username_field)})

            if not user:
                msg = _('No such user.')
                raise serializers.ValidationError(msg)
            else:
                msg = _('Incorrect password.')
                raise serializers.ValidationError(msg)
        return response


class UserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(
        allow_null=False,
        allow_blank=False,
        required=False
    )


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=6, max_length=40)
    new_password = serializers.CharField(min_length=6, max_length=40)
