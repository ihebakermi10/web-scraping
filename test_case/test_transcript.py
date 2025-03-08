import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API Google depuis l'environnement
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("La clé API Google est manquante. Veuillez définir GOOGLE_API_KEY dans votre fichier .env")

# Initialiser le client Gemini avec la clé API
genai.configure(api_key=GOOGLE_API_KEY)

def transcrire_audio(base64_audio: str) -> str:
    """
    Décode l'audio encodé en base64, crée un Part inline et demande à Gemini de transcrire l'audio.
    
    Args:
        base64_audio (str): L'audio encodé en base64.
    
    Returns:
        str: La transcription renvoyée par l'API Gemini.
    """
    # Décoder la chaîne base64 en données binaires
    audio_bytes = base64.b64decode(base64_audio)
    
    # Créer un Part pour les données audio inline
    # Ici on suppose que l'audio est au format WAV, sinon modifiez le mime_type (ex. 'audio/mp3')
    audio_part = genai.types.Part.from_bytes(
        data=audio_bytes,
        mime_type='audio/wav'
    )
    
    # Définir le prompt pour demander la transcription
    prompt = "Transcris le contenu de cet extrait audio en texte."
    
    # Appeler l'API Gemini Flash 2.0 pour générer du contenu à partir du prompt et de l'audio
    response = genai.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, audio_part]
    )
    
    return response.text

if __name__ == "__main__":
    # Exemple de segment audio encodé en base64 (extrait de votre script)
    audio_segment = (
        "//9/f39/f3////////9/f39/f39//3///v//////fn//f39/////fn7//////3///////39/f"
        "///////////////f//////////+//////9/f39/f39/f39//39///9//39/f3///////////v7//////39/f39/f/9/f39///////9/f/9///9/f///f39/f3////////7//v///n9/fw=="
    )
    
    try:
        transcription = transcrire_audio(audio_segment)
        print("Transcription :", transcription)
    except Exception as e:
        print("Erreur lors de la transcription :", e)