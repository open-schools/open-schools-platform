from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.user_management.users.serializers import CreationTokenSerializer
from open_schools_platform.user_management.users.services import create_token
from open_schools_platform.utils.firebase_requests import send_firebase_sms


def valid_token_for_tests_creation(data):

    token_serializer = CreationTokenSerializer(data=data)
    token_serializer.is_valid(raise_exception=True)
    response_for_token = send_firebase_sms(**token_serializer.data)
    token = create_token(token_serializer.validated_data["phone"],
                         get_dict_from_response(response_for_token)["sessionInfo"])
    return token
