from firebase_admin import messaging

from open_schools_platform.common.firebase.settings import app
from open_schools_platform.user_management.users.models import User


def notify_user(user: User, title: str, body: str, data: dict = None):
    if user.firebase_token.token is not None:
        message = messaging.Message(
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(title=title, body=body)),
            data=data,
            token=user.firebase_token.token,
        )
        messaging.send(message, app=app)
