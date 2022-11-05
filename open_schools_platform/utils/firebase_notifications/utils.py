from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from open_schools_platform.utils.firebase_notifications.settings import app
from open_schools_platform.user_management.users.models import User


def notify_user(user: User, title: str, body: str, data: dict = None):

    """
    notify_user returns numeric values if it fails:
        0 - User has no firebase registration token
        1 - Error occurred while sending push notification
        2 - notification was sent successfully
    """

    if user.firebase_token.token is None:
        return 0
    message = messaging.Message(
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(title=title, body=body)),
        data=data,
        token=user.firebase_token.token,
    )
    try:
        messaging.send(message, app=app)
    except FirebaseError or ValueError:
        return 1
    return 2
