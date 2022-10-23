import os

import firebase_admin

from firebase_admin import credentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FIREBASE_API_KEY = os.path.join(BASE_DIR, "firebase_key.json")

cred = credentials.Certificate(FIREBASE_API_KEY)
app = firebase_admin.initialize_app(cred)
