import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials

BASE_DIR = Path(__file__).resolve().parent.parent

service_account_path = os.getenv(
    "FIREBASE_CREDENTIALS",
    str(BASE_DIR / "serviceAccountKey.json")
)

cred = credentials.Certificate(service_account_path)

firebase_admin.initialize_app(cred)