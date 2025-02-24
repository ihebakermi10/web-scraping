
import os
from motor.motor_asyncio import AsyncIOMotorClient
from .config import SYSTEM_MESSAGE

async def get_prompt_for_number(phone_number: str) -> str:
    
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "nehos")
    collection_name = os.getenv("COLLECTION_NAME", "client")
    
    if not mongo_uri:
        print("MONGO_URI non défini. Utilisation de SYSTEM_MESSAGE par défaut.")
        return SYSTEM_MESSAGE
    
    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        try:
            phone_identifier = int(phone_number)
        except ValueError:
            phone_identifier = phone_number
        
        document = await collection.find_one({"numero": phone_identifier})
        if document and "system_message" in document:
            return document["system_message"]
        else:
            print(f"Aucun system_message trouvé pour le numéro {phone_number}.")
            return SYSTEM_MESSAGE
    except Exception as error:
        print("Erreur lors de la récupération du system_message depuis MongoDB :", error)
        return SYSTEM_MESSAGE
