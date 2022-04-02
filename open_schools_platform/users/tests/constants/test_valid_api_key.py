import json

import requests


def is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
    base_url = FIREBASE_URL_TO_GET_SESSION + \
               GOOGLE_API_KEY

    response = requests.post(base_url)
    try:
        status = json.loads(response.content.decode("utf-8"))['error']['status']
    except:
        return True

    return "INVALID_ARGUMENT" != status
    
