import os
from pymongo import MongoClient

def store_genai_result(genai_result):
   
    MONGO_URI ="mongodb+srv://user:J8ka9k6gROdq41Wo@cluster0.7qmmbmw.mongodb.net/"
    if not MONGO_URI:
        raise ValueError("La variable d'environnement MONGO_URI n'est pas définie.")
    
    client = MongoClient(MONGO_URI)
    db = client["nehos"]        
    collection = db["client"]     

    

    result = collection.insert_one(genai_result)
    print(f"Document inséré avec l'id: {result.inserted_id}")
