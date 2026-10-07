from dotenv import load_dotenv
import os

load_dotenv()

sarvam_api=os.getenv("SARVAM_APIKEY")
DATABASE_NAME=os.getenv("DATABASE_NAME")
MONGODB_URL=os.getenv("MONGODB_URL")
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY")
