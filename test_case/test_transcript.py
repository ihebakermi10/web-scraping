import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("La clé API Google est manquante. Veuillez définir GOOGLE_API_KEY dans votre fichier .env")

genai.configure(api_key=GOOGLE_API_KEY)

def transcrire_audio(base64_audio: str) -> str:

    audio_bytes = base64.b64decode(base64_audio)

    audio_part = genai.types.Part.from_bytes(
        data=audio_bytes,
        mime_type='audio/wav'
    )
    
    prompt = "Transcris le contenu de cet extrait audio en texte."
    
    response = genai.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, audio_part]
    )
    
    return response.text

if __name__ == "__main__":
    audio_segment = (
        "//9/f39/f3////////9/f39/f39//3///v//////fn//f39/////fn7//////3///////39/f"
        "///////////////f//////////+//////9/f39/f39/f39//39///9//39/f3///////////v7//////39/f39/f/9/f39///////9/f/9///9/f///f39/f3////////7//v///n9/fw=="
    )
    
    try:
        transcription = transcrire_audio(audio_segment)
        print("Transcription :", transcription)
    except Exception as e:
        print("Erreur lors de la transcription :", e)