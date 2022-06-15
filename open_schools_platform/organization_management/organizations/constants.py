from open_schools_platform.common.constants import CommonConstants


class OrganizationConstants:
    @staticmethod
    def get_invite_message(phone: str, pwd: str) -> str:
        phone = phone.replace('+', '')
        INVITE_SMS_MESSAGE = "Тел: +{phone}\n" \
                             "Пароль: {pwd}\n" \
                             "-> " + CommonConstants.SCHOOLS_AI_URL

        return INVITE_SMS_MESSAGE.format(phone=phone, pwd=pwd)
