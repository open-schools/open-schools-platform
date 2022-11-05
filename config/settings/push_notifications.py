import os
import sys

import firebase_admin

from firebase_admin import credentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

frame = sys._getframe()

FIREBASE_ADMIN_CONFIG = os.path.join(os.path.dirname(frame.f_back.f_code.co_filename), 'firebase_admin_config.json')

if not os.path.exists(FIREBASE_ADMIN_CONFIG):
    raise FileNotFoundError("Create firebase_key file")

cred = credentials.Certificate(FIREBASE_ADMIN_CONFIG)
app = firebase_admin.initialize_app(cred)
