
from rest_framework import serializers

from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.compat import gettext_lazy as _
from open_schools_platform.user_management.users.selectors import get_user


class JSONWebTokenWithTwoResponses(JSONWebTokenSerializer):

    def validate(self, data):
        try:
            response = super().validate(data)
        except serializers.ValidationError:
            user = get_user(filters={"phone": data.get(self.username_field)})

            if not user:
                msg = _('No such user.')
                raise serializers.ValidationError(msg)
            else:
                msg = _('Incorrect password.')
                raise serializers.ValidationError(msg)
        return response
