from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.user_management.users.models import CreationToken, User
from open_schools_platform.user_management.users.serializers import CreateRegistrationTokenSerializer
from open_schools_platform.user_management.users.services import create_token
from open_schools_platform.utils.firebase_requests import send_firebase_sms
from open_schools_platform.user_management.users.services import create_user


def create_logged_in_user(instance):
    credentials = {
        "phone": "+79025456481",
        "password": "123456",
        "name": "test_user"
    }

    user = create_user(**credentials)
    instance.client.login(**credentials)
    return user


def create_test_user(phone: str = "+79025456481") -> User:
    user = create_user(
        phone=phone,
        password="123456",
        name="test_user"
    )
    return user


def create_test_token(phone: str = "+79020000000") -> CreationToken:
    # session used in here is invalid
    data = {
        "phone": phone,
        "session": "000000"
    }
    token = create_token(**data)
    return token


def create_valid_test_token() -> CreationToken:
    # make sure this number is listed in firebase
    data = {
        "phone": "+79025456481",
        "recaptcha": "123456"
    }
    token_serializer = CreateRegistrationTokenSerializer(data=data)
    token_serializer.is_valid(raise_exception=True)
    response_for_token = send_firebase_sms(**token_serializer.data)
    token = create_token(token_serializer.validated_data["phone"],
                         get_dict_from_response(response_for_token)["sessionInfo"])
    return token
