import os
import json
import base64
import audioop
import re
from pydub import AudioSegment

# Import de l'API Gemini
from google.genai import Client, types

# Nom du fichier de base de données
DATABASE_FILENAME = "Database.json"

def load_database():
    """Charge le fichier JSON de la base de données."""
    if not os.path.exists(DATABASE_FILENAME):
        print(f"Le fichier {DATABASE_FILENAME} n'existe pas.")
        return {}
    with open(DATABASE_FILENAME, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_call_conversation(call_id):
    """
    Parcourt la base de données pour trouver la conversation correspondant au call_id.
    La structure attendue est :
    db["users"][<from_number>][<call_id>] = {
         ...,
         "conversation_log": [list of chunks]
    }
    """
    db = load_database()
    for user, calls in db.get("users", {}).items():
        if call_id in calls:
            call_record = calls[call_id]
            conversation = call_record.get("conversation_log", [])
            return user, conversation
    return None, None

def process_conversation(conversation):
    """
    Combine les segments audio dans l'ordre d'insertion de la conversation_log.
    Avant la conversion, on limite les longues séquences de silence (octets 0xFF)
    en les remplaçant par seulement deux octets 0xFF.
    Ici, aucune pause n'est ajoutée entre les segments.
    """
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
            # Décodage de la chaîne base64 pour obtenir les données u-law
            ulaw_data = base64.b64decode(audio_b64)
            # Limiter les longues séquences de silence (octets 0xFF)
            ulaw_data = re.sub(b'\xff{3,}', b'\xff\xff', ulaw_data)
        except Exception as e:
            print(f"Erreur de décodage base64 pour le chunk à {timestamp} : {e}")
            continue

        try:
            # Conversion de u-law vers PCM linéaire (16 bits = 2 octets)
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

        # Ici, nous n'ajoutons pas de silence (duration=0)
        if previous_speaker is not None and speaker != previous_speaker:
            silence = AudioSegment.silent(duration=0)
            combined_audio += silence

        combined_audio += segment
        previous_speaker = speaker

    return combined_audio

def save_audio(audio_segment, output_filename):
    """Exporte le segment audio combiné dans un fichier WAV."""
    audio_segment.export(output_filename, format="wav")
    print(f"Audio combiné sauvegardé dans {output_filename}")

def transcribe_audio_with_gemini(audio_filepath):
    """
    Utilise l'API Gemini pour obtenir une transcription complète de l'audio.
    Le fichier audio est lu en mode binaire, puis fourni en inline dans la requête.
    """
    client = Client(api_key = "AIzaSyBs_CEsN0b8RnD9Wx6z5qvf_Jl0Kz3NGXk")
    with open(audio_filepath, "rb") as f:
        audio_bytes = f.read()
    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type="audio/wav"  # Ajustez le MIME type si nécessaire
    )
    prompt = "Please provide a full transcription of the speech in this audio clip."
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, audio_part]
    )
    return response.text

def main():
    # Remplacez call_id par celui souhaité
    call_id = "CA576203a84fa6b43d70a444ba67425557"
    user, conversation = extract_call_conversation(call_id)
    if conversation is None:
        print(f"Call ID {call_id} non trouvé dans la base de données.")
        return

    print(f"Traitement de la conversation pour le call ID {call_id} (utilisateur: {user}).")
    combined_audio = process_conversation(conversation)
    output_filename = f"conversation_{call_id}.wav"
    save_audio(combined_audio, output_filename)

    print("Transcription en cours via l'API Gemini...")
    transcription = transcribe_audio_with_gemini(output_filename)
    print("Transcription complète de l'audio :\n")
    print(transcription)

if __name__ == "__main__":
    main()