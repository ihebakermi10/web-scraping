
import os
import base64
import wave
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB")
COLLECTION_SPEECH = os.getenv("COLLECTION_SPEECH")

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    speech_collection = db[COLLECTION_SPEECH]
    print("Connexion MongoDB établie avec succès.")
except Exception as e:
    print("Erreur lors de la connexion à MongoDB :", e)
    exit(1)

document = speech_collection.find_one(sort=[("recording_time", -1)])
if not document:
    print("Aucun document trouvé dans la collection.")
    exit(1)
if "all_audio_chunks" not in document:
    print("Le document ne contient pas le champ 'all_audio_chunks'.")
    exit(1)

all_audio_chunks = document["all_audio_chunks"]
print(f"Nombre de chunks récupérés : {len(all_audio_chunks)}")

print("Début du traitement final de l'audio...")
try:
    complete_audio_bytes = b"".join([base64.b64decode(chunk) for chunk in all_audio_chunks])
    print(f"Taille du flux audio fusionné (en octets) : {len(complete_audio_bytes)}")
    print("Audio complet de la conversation fusionné correctement.")
except Exception as merge_err:
    print("Erreur lors de la fusion des chunks audio:", merge_err)
    complete_audio_bytes = b""

try:
    filename = "merged_audio.wav"
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)     
        wf.setsampwidth(1)      
        wf.setframerate(8000)   
        wf.writeframes(complete_audio_bytes)
    print(f"Audio complet sauvegardé localement sous '{filename}'")
except Exception as e:
    print("Erreur lors de la sauvegarde du fichier audio :", e)
