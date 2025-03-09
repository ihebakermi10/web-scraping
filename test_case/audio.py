
import os
import json
import base64
import audioop
import io
from pydub import AudioSegment

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
    La structure est supposée être : db["users"][<from_number>][<call_id>] = [list of chunks]
    """
    db = load_database()
    for user, calls in db.get("users", {}).items():
        if call_id in calls:
            conversation = calls[call_id]
            return user, conversation
    return None, None

def process_conversation(conversation):

    conversation_sorted = sorted(conversation, key=lambda x: x["timestamp"])
    combined_audio = AudioSegment.empty()
    previous_speaker = None

    for chunk in conversation_sorted:
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
            silence = AudioSegment.silent(duration=500)  
            combined_audio += silence

        combined_audio += segment
        previous_speaker = speaker

    return combined_audio

def save_audio(audio_segment, output_filename):
    """Exporte le segment audio combiné dans un fichier WAV."""
    audio_segment.export(output_filename, format="wav")
    print(f"Audio combiné sauvegardé dans {output_filename}")

def main():
    call_id = "CAcf14e179d46ea8a8f1f7c914e00e94f5"
    user, conversation = extract_call_conversation(call_id)
    if conversation is None:
        print(f"Call ID {call_id} non trouvé dans la base de données.")
        return

    print(f"Traitement de la conversation pour le call ID {call_id} (utilisateur: {user}).")
    combined_audio = process_conversation(conversation)
    output_filename = f"conversation_{call_id}.wav"
    save_audio(combined_audio, output_filename)

if __name__ == "__main__":
    main()
