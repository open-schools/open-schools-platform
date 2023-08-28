from open_schools_platform.common.constants import CommonConstants
from django.utils.translation import gettext_lazy as _


class OrganizationConstants:
    @staticmethod
    def get_invite_message(phone, pwd):
        phone = phone.replace('+', '')
        INVITE_SMS_MESSAGE = \
            _('Phone: +{phone}\n') + _('Password: {pwd}\n') + "-> " + CommonConstants.OPEN_SCHOOLS_DOMAIN

        return INVITE_SMS_MESSAGE.format(phone=phone, pwd=pwd)
