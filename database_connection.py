import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    from pymongo import MongoClient

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv('MONGO_CONNECTION')

    # Create a connection using MongoClient
    client = MongoClient(CONNECTION_STRING)
    db = client.career
    return db