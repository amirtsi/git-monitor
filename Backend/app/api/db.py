import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from bson import ObjectId
import logging
from datetime import datetime

# Configure basic logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    client: MongoClient = None

db = Database()

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logging.info("Disconnected from MongoDB Atlas")

async def connect_to_mongo():
    try:
        uri = os.getenv("DATABASE_URL")
        tls_certificate_path = os.getenv("TLSCERTIFICATEKEYFILE")
        db_name = os.getenv("DB_NAME")
        
        if not uri:
            logging.error("DATABASE_URL environment variable is not set")
            raise ValueError("DATABASE_URL environment variable is not set")
        if not tls_certificate_path:
            logging.error("TLSCERTIFICATEKEYFILE environment variable is not set")
            raise ValueError("TLSCERTIFICATEKEYFILE environment variable is not set")
        if not db_name:
            logging.error("DB_NAME environment variable is not set")
            raise ValueError("DB_NAME environment variable is not set")
        
        db.client = MongoClient(uri, tls=True, tlsCertificateKeyFile=tls_certificate_path, server_api=ServerApi('1'))
        db.client.admin.command('ping')
        logging.info("Connected to MongoDB Atlas")
    except OperationFailure as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        await close_mongo_connection()

async def save_data(data: dict, screenshot_path: str):
    try:
        collection_name = os.getenv("COLLECTION_NAME")
        if not collection_name:
            logging.error("COLLECTION_NAME environment variable is not set")
            raise ValueError("COLLECTION_NAME environment variable is not set")
        
        collection = db.client[os.getenv("DB_NAME")][collection_name]
        
        # Add the current date to the data dictionary
        data['date'] = datetime.utcnow()
        data['screenshot_path'] = screenshot_path
        
        result = collection.insert_one(data)
        logging.info(f"Data saved to {collection_name}. Document ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logging.error(f"Error saving data to {collection_name}: {e}")
        return None

async def check_mongo_connection():
    try:
        db.client.admin.command('ping')
        return True
    except OperationFailure as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        return False

async def get_all_objects():
    try:
        collection_name = os.getenv("COLLECTION_NAME")
        if not collection_name:
            logging.error("COLLECTION_NAME environment variable is not set")
            raise ValueError("COLLECTION_NAME environment variable is not set")
        
        collection = db.client[os.getenv("DB_NAME")][collection_name]
        objects = collection.find({})
        objects_list = []
        for obj in objects:
            pr = {
                "id": str(obj["_id"]),
                "title": obj.get("html_url", ""),
                "user": obj.get("user", ""),
                "screenshot_path": obj.get("screenshot_path", ""),
                "date": obj.get("date", datetime.utcnow())  # Default to current UTC time if date is not present
            }
            objects_list.append(pr)
        return objects_list
    except Exception as e:
        logging.error(f"Error retrieving objects: {e}")
        raise e
