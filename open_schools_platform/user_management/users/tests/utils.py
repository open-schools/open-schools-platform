from open_schools_platform.user_management.users.models import CreationToken, User
from open_schools_platform.user_management.users.serializers import CreateRegistrationTokenSerializer
from open_schools_platform.user_management.users.services import create_token
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
    data = {
        "phone": phone,
        "otp": "000000"
    }
    token = create_token(str(data["phone"]), int(data["otp"]))
    return token


def create_valid_test_token() -> CreationToken:
    data = {
        "phone": "+79025456481",
        "recaptcha": "123456"
    }
    token_serializer = CreateRegistrationTokenSerializer(data=data)
    token_serializer.is_valid(raise_exception=True)
    token = create_token(token_serializer.validated_data["phone"], 123456)
    return token
