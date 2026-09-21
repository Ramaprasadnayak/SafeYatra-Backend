import os
import json

import firebase_admin
from firebase_admin import credentials

firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if not firebase_json:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT environment variable is not set")

cred = credentials.Certificate(json.loads(firebase_json))

firebase_admin.initialize_app(cred)