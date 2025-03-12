import os
import json
import base64
import audioop
import re
from fastapi import APIRouter, HTTPException
from pydub import AudioSegment

from google.genai import Client, types

router = APIRouter()

DATABASE_FILENAME = "Database.json"

def load_database():
    """Charge le fichier JSON de la base de données."""
    if not os.path.exists(DATABASE_FILENAME):
        print(f"Le fichier {DATABASE_FILENAME} n'existe pas.")
        return {}
    with open(DATABASE_FILENAME, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_call_conversation(call_id: str):
 
    db = load_database()
    for user, calls in db.get("users", {}).items():
        if call_id in calls:
            call_record = calls[call_id]
            conversation = call_record.get("conversation_log", [])
            return user, conversation
    return None, None

def process_conversation(conversation):

    combined_audio = AudioSegment.empty()
    previous_speaker = None

    for chunk in conversation:
        speaker = chunk.get("speaker")
        audio_b64 = chunk.get("audio")
        timestamp = chunk.get("timestamp")
        if not audio_b64:
            print(f"Aucun audio trouvé pour le chunk à {timestamp}")
            continue

        try:
            ulaw_data = base64.b64decode(audio_b64)
        except Exception as e:
            print(f"Erreur de décodage base64 pour le chunk à {timestamp} : {e}")
            continue

        try:
            linear_pcm = audioop.ulaw2lin(ulaw_data, 2)
        except Exception as e:
            print(f"Erreur de conversion ulaw->PCM pour le chunk à {timestamp} : {e}")
            continue

        segment = AudioSegment(
            data=linear_pcm,
            sample_width=2,
            frame_rate=8000,
            channels=1
        )

        if previous_speaker is not None and speaker != previous_speaker:
            silence = AudioSegment.silent(duration=0)
            combined_audio += silence

        combined_audio += segment
        previous_speaker = speaker

    return combined_audio

def save_audio(audio_segment, output_filename):
    """Exporte l'audio combiné dans un fichier WAV."""
    audio_segment.export(output_filename, format="wav")
    print(f"Audio combiné sauvegardé dans {output_filename}")

def transcribe_audio_with_gemini(audio_filepath):

    client = Client(api_key="AIzaSyBs_CEsN0b8RnD9Wx6z5qvf_Jl0Kz3NGXk")
    with open(audio_filepath, "rb") as f:
        audio_bytes = f.read()
    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type="audio/wav" 
    )
    prompt = "Please provide a full transcription of the speech in this audio clip."
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, audio_part]
    )
    return response.text

@router.get("/transcription/{call_id}")
async def get_transcription(call_id: str):

    user, conversation = extract_call_conversation(call_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail=f"Call ID {call_id} non trouvé dans la base de données.")
    
    combined_audio = process_conversation(conversation)
    output_filename = f"conversation_{call_id}.wav"
    save_audio(combined_audio, output_filename)
    
    transcription = transcribe_audio_with_gemini(output_filename)
    
    return {"id": call_id, "transcription": transcription}
