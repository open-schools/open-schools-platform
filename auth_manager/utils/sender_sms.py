import json
import requests as re

googleAPIKey = "AIzaSyDMUyN4rWYXnhihnIOBYBQvA--81EsGPQ8"

def prepare_phone_number(phone_number):
    for char in r" -()":
        phone_number = phone_number.replace(char, "")
    if phone_number[0] == "8":
        phone_number = "+7" + phone_number[1:]
    if phone_number[0] == "7":
        phone_number = "+" + phone_number
    return phone_number


def send_sms(phone_number, recaptcha):
    number = prepare_phone_number(phone_number)
    base_url = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key="+googleAPIKey

    dict = {
        "phoneNumber": number,
        "recaptchaToken": recaptcha,
    }

    response = re.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return json.loads(response.content.decode("utf-8"))["sessionInfo"]
