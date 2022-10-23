from firebase_admin import messaging

from open_schools_platform.common.firebase.settings import app
from open_schools_platform.user_management.users.models import User


def notify_user(user: User, title, body):
    if user.firebase_token is not None:
        message = messaging.Message(
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(title=title, body=body)), token=user.firebase_token,
        )
        messaging.send(message, app=app)
