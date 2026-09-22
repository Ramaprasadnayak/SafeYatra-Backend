from dotenv import load_dotenv
import os

load_dotenv()

sarvam_api=os.getenv("SARVAM_APIKEY")
DATABASE_NAME=os.getenv("DATABASE_NAME")
MONGODB_URL=os.getenv("MONGODB_URL")