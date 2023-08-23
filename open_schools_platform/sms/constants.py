from environ import ImproperlyConfigured

from config.env import env


class SmsConstants:
    LOGIN = env('SMS_LOGIN', default=None)
    PASSWORD = env('SMS_PASSWORD', default=None)

    LINK_TO_PARENT = env('SMS_LINK_TO_PARENT', default=None)
    LINK_TO_EMPLOYEE = env('SMS_LINK_TO_EMPLOYEE', default=None)

    if LINK_TO_PARENT and len(LINK_TO_PARENT) > 14:
        raise ImproperlyConfigured('SMS_LINK_TO_PARENT env is too big')
    if LINK_TO_EMPLOYEE and len(LINK_TO_EMPLOYEE) > 50:
        raise ImproperlyConfigured('SMS_LINK_TO_EMPLOYEE env is too big')

    INVITE_PARENT_MESSAGE = '{name}:\n{link}\nпароль: {password}'
    INVITE_EMPLOYEE_MESSAGE = '{phone}\n{password}\n-> {link}'

    MAX_NAME_LENGTH = 27
    MAX_PHONE_LENGTH = 12
    PASSWORD_MAX_LENGTH = 8
