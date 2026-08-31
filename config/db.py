from config.settings import (MONGODB_URL,DATABASE_NAME)
from pymongo import MongoClient

client = MongoClient(MONGODB_URL)

db = client[DATABASE_NAME]
users_collection = db["users"]
 