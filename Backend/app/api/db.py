import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from bson import ObjectId

class Database:
    client: MongoClient = None

db = Database()

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB Atlas")

async def connect_to_mongo():
    try:
        uri = os.getenv("DATABASE_URL")
        tls_certificate_path = os.getenv("TLSCERTIFICATEKEYFILE")
        db_name = os.getenv("DB_NAME")
        
        if not uri:
            raise ValueError("DATABASE_URL environment variable is not set")
        if not tls_certificate_path:
            raise ValueError("TLSCERTIFICATEKEYFILE environment variable is not set")
        if not db_name:
            raise ValueError("DB_NAME environment variable is not set")
        
        # Connect to MongoDB Atlas with TLS/SSL authentication
        db.client = MongoClient(uri,
                                tls=True,
                                tlsCertificateKeyFile=tls_certificate_path,
                                server_api=ServerApi('1'))
        
        # Check if the connection is successful
        db.client.admin.command('ping')
        
        print("Connected to MongoDB Atlas")
    except OperationFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        await close_mongo_connection()

async def save_data(data: dict, screenshot_path: str):
    try:
        collection_name = os.getenv("COLLECTION_NAME")
        if not collection_name:
            raise ValueError("COLLECTION_NAME environment variable is not set")
        
        collection = db.client[os.getenv("DB_NAME")][collection_name]
        
        # Add the screenshot path to the data dictionary
        data['screenshot_path'] = screenshot_path
        
        print(f"Inserting data into collection {collection_name}: {data}")
        result = collection.insert_one(data)
        print(f"Data saved to {collection_name}. Document ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"Error saving data to {collection_name}: {e}")
        return None

async def check_mongo_connection():
    try:
        # Check if the connection is active
        db.client.admin.command('ping')
        return True
    except OperationFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

async def get_all_objects():
    try:
        collection_name = os.getenv("COLLECTION_NAME")
        if not collection_name:
            raise ValueError("COLLECTION_NAME environment variable is not set")
        
        collection = db.client[os.getenv("DB_NAME")][collection_name]
        
        # Retrieve all objects from the collection
        objects = collection.find({})
        
        # Convert MongoDB cursor to list of dictionaries
        objects_list = []
        for obj in objects:
            # Map the properties to match the expected structure
            pr = {
                "id": str(obj["_id"]),  # Convert ObjectId to string
                "title": obj.get("html_url", ""),  # Assuming html_url is a property in the object
                "user": obj.get("user", ""),  # Assuming user is a property in the object
                "screenshot_path": obj.get("screenshot_path", ""),  # Assuming screenshot_path is a property in the object
            }
            objects_list.append(pr)
        
        return objects_list
    except Exception as e:
        raise e