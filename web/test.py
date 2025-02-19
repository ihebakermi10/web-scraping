#!/usr/bin/env python3
import os
from pymongo import MongoClient

def test_db():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    if not mongo_uri or not db_name or not collection_name:
        print("Erreur : Les variables d'environnement MONGO_URI, DB_NAME et COLLECTION_NAME doivent être définies.")
        return

    try:
        client = MongoClient(mongo_uri)
        db = client["nehos"]
        collection = db["client"]
        print(f"Connecté à la DB '{db_name}' et à la collection '{collection_name}'.")

        test_doc = {
            "test_field": "test_value",
            "number": 42
        }
        insert_result = collection.insert_one(test_doc)
        print(f"Document inséré avec l'id : {insert_result.inserted_id}")

        # Récupération du document inséré
        retrieved_doc = collection.find_one({"_id": insert_result.inserted_id})
        print("Document récupéré :")
        print(retrieved_doc)

        # Suppression du document de test
         #delete_result = collection.delete_one({"_id": insert_result.inserted_id})
        #print(f"Documents supprimés : {delete_result.deleted_count}")

        print("Test de la base de données terminé avec succès.")

    except Exception as e:
        print("Une erreur est survenue lors du test de la base de données :")
        print(e)

if __name__ == "__main__":
    test_db()
