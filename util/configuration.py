import os

from pymongo.errors import ConnectionFailure
from pymongo.mongo_client import MongoClient

uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
database = os.getenv("MONGO_DATABASE", "iiot")
client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("MongoDB Connection Successful")
except ConnectionFailure:
    print("Failed to connect to Mongodb Server")

if client:
    print("MongoDB connection established successfully")
    db = client.get_database(database)
    print(db)
    user_col = db["user"]
