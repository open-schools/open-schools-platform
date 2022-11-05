import json

import firebase_admin

from firebase_admin import credentials

from open_schools_platform.common.constants import CommonConstants

FCM_API_KEY = json.loads(CommonConstants.FIREBASE_ADMIN_CONFIG)   # type: ignore
cred = credentials.Certificate(FCM_API_KEY)
app = firebase_admin.initialize_app(cred)
