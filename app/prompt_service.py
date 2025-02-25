
import os
from motor.motor_asyncio import AsyncIOMotorClient
async def get_prompt_for_number(phone_number: str) -> str:
    
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "nehos")
    collection_name = os.getenv("COLLECTION_NAME", "client")
    
    if not mongo_uri:
        print("MONGO_URI non defini. Utilisation de SYSTEM_MESSAGE par défaut.")
    print("Recherche pour numero :" , phone_number)
    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        phone_number_clean = phone_number.lstrip('+')
        print(f"Recherche du system_message pour le numero {phone_number_clean}...")
        try:
            phone_identifier = int(phone_number_clean)
        except ValueError:
            phone_identifier = phone_number_clean
        
        document = await collection.find_one({"numero": phone_identifier})
        if document and "system_message" in document:
            return document["system_message"]
        else:
            print(f"Aucun system_message trouve pour le numéro {phone_number_clean}.")
            return ""
    except Exception as error:
        print("Erreur lors de la recuperation du system_message depuis MongoDB :", error)
        return ""
