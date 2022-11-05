import requests
from open_schools_platform.common.constants import CommonConstants


def is_firebase_token_valid(token: str,):
    url = CommonConstants.FCM_URL_TO_VALIDATE_NOTIFICATIONS_TOKEN.format(token=token)
    headers = {
        'Authorization': f'key={CommonConstants.FCM_SERVER_KEY}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return False
    return True
