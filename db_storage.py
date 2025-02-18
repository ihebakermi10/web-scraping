import os
from pymongo import MongoClient

def store_results_in_db(domain: str, scraped_data: dict, number_phone: str, email: str, category: str, genai_result: list):
  
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI)
    db = client["nehos"]
    collection = db["client"]

    document = {
        "domain": domain,
        "scraped_data": scraped_data,
        "number_phone": number_phone,
        "email": email,
        "category": category,
        "genai_result": genai_result
    }

    result = collection.insert_one(document)
    print(f"Document inséré avec l'id: {result.inserted_id}")
