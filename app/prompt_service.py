import os
from motor.motor_asyncio import AsyncIOMotorClient

async def get_prompt_for_number(phone_number: str) -> str:
    
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "nehos")
    collection_name = os.getenv("COLLECTION_NAME", "client")
    
    if not mongo_uri:
        print("MONGO_URI not defined. Using default SYSTEM_MESSAGE.")
    print("Searching for number:", phone_number)
    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        phone_number_clean = phone_number.lstrip('+')
        print(f"Searching for system_message for number {phone_number_clean}...")
        try:
            phone_identifier = int(phone_number_clean)
        except ValueError:
            phone_identifier = phone_number_clean
        
        document = await collection.find_one({"numero": phone_identifier})
        if document and "system_message" in document:
            return document["system_message"]
        else:
            print(f"No system_message found for number {phone_number_clean}.")
            return ""
    except Exception as error:
        print("Error retrieving system_message from MongoDB:", error)
        return ""
