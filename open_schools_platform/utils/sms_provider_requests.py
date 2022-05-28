from typing import List

import requests

from open_schools_platform.common.constants import CommonConstants


def prepare_phone_number(phone: str):
    phone = str(phone)  # PhoneNumber cast

    # TODO: check if it works in different countries
    if phone[0] == '+':
        return phone[1:len(phone)]


def send_sms(*, to: List[str], msg: str):
    """
    Send sms to defined phones with msg body
    """

    base_url = "{url}/?api_id={api_key}".format(url=CommonConstants.SMS_PROVIDER_URL,
                                                api_key=CommonConstants.SMS_API_KEY)

    phones = ""
    for phone in to:
        phones += "&to[{phone}]={msg}".format(phone=prepare_phone_number(phone), msg=msg)

    url = base_url + phones + "&json=1&from=LamArt"

    response = requests.get(url)

    return dict(map(
        lambda phone: ('+' + phone, int(response.json()["sms"][phone]["status_code"])),
        response.json()["sms"]))
