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
    print("MongoDB connection established successfully.")
except Exception as e:
    print("Error connecting to MongoDB:", e)
    exit(1)

document = speech_collection.find_one(sort=[("recording_time", -1)])
if not document:
    print("No document found in the collection.")
    exit(1)
if "all_audio_chunks" not in document:
    print("The document does not contain the field 'all_audio_chunks'.")
    exit(1)

all_audio_chunks = document["all_audio_chunks"]
print(f"Number of chunks retrieved: {len(all_audio_chunks)}")

print("Starting final audio processing...")
try:
    complete_audio_bytes = b"".join([base64.b64decode(chunk) for chunk in all_audio_chunks])
    print(f"Merged audio stream size (in bytes): {len(complete_audio_bytes)}")
    print("Complete conversation audio merged successfully.")
except Exception as merge_err:
    print("Error merging audio chunks:", merge_err)
    complete_audio_bytes = b""

try:
    filename = "merged_audio.wav"
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(8000)
        wf.writeframes(complete_audio_bytes)
    print(f"Complete audio saved locally as '{filename}'")
except Exception as e:
    print("Error saving audio file:", e)
