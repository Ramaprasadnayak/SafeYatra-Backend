from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_NAME=os.getenv("DATABASE_NAME")
MONGODB_URL=os.getenv("MONGODB_URL")