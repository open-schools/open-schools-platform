import json
from urllib.parse import urlencode

import requests

from open_schools_platform.errors.exceptions import SmsServiceUnavailable
from open_schools_platform.sms.constants import SmsConstants


def crop_name(name):
    max_length = SmsConstants.MAX_NAME_LENGTH
    if len(name) > max_length:
        return name[:max_length - 3] + '...'
    return name


def valid_sms(login, sms_password, phone, user_password, link):
    return (link and login and sms_password
            and len(phone) <= SmsConstants.MAX_PHONE_LENGTH and len(user_password) <= SmsConstants.PASSWORD_MAX_LENGTH)


def send_sms_to_parent(phone, name, user_password):
    login = SmsConstants.LOGIN
    sms_password = SmsConstants.PASSWORD
    link = SmsConstants.LINK_TO_PARENT
    if not valid_sms(login, sms_password, phone, user_password, link):
        raise SmsServiceUnavailable

    message = SmsConstants.INVITE_PARENT_MESSAGE.format(name=crop_name(name), link=link, password=user_password)
    sender = SmsSender(login, sms_password)
    sender.send(phone, message)


def send_sms_to_employee(phone, user_password):
    login = SmsConstants.LOGIN
    sms_password = SmsConstants.PASSWORD
    link = SmsConstants.LINK_TO_EMPLOYEE
    if not valid_sms(login, sms_password, phone, user_password, link):
        raise SmsServiceUnavailable

    message = SmsConstants.INVITE_EMPLOYEE_MESSAGE.format(phone=phone, link=link, password=user_password)
    sender = SmsSender(login, sms_password)
    sender.send(phone, message)


class SmsSender:
    def __init__(self, login, password):
        self.host = 'api.prostor-sms.ru/messages/v2'
        self.login_data = dict({"login": login, "password": password})

    def get_balance(self):
        response = requests.post(self._get_url('balance.json'), data=self.login_data)
        return response

    def send(self, phone, text, client_id=None):
        sender = self._get_senders()[0]['name']
        data = {
            **self.login_data,
            "showBillingDetails": True,
            "messages": [
                {
                    "phone": phone,
                    "sender": sender,
                    "text": text,
                    "clientId": client_id
                }
            ]
        }
        return requests.post(self._get_url('send.json'), data=json.dumps(data))

    def _get_senders(self):
        response = requests.post(self._get_url('senders.json'), data=self.login_data)
        if response.status_code == 200:
            return response.json()['senders']
        return None

    def _get_url(self, path, params=None):
        url = f'http://{self.host}/{path}/'
        param_str = ''
        if params is not None:
            for k, v in params.items():
                if v is None:
                    del params[k]
            param_str = urlencode(params)
        return f'{url}?{param_str}'
