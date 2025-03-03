from dotenv import load_dotenv
import os
from twilio.rest import Client
import requests

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les identifiants depuis le fichier .env
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

# Récupérer la liste des enregistrements (limitée au plus récent)
recordings = client.recordings.list(limit=1)

if not recordings:
    print("Aucun enregistrement trouvé.")
else:
    recording = recordings[0]
    print("SID de l'enregistrement :", recording.sid)
    
    # Construire l'URL de téléchargement du fichier audio
    # L'URI fournie par l'API se termine par .json, on le remplace par .wav pour obtenir le fichier audio
    recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.wav')}"
    print("Téléchargement de l'enregistrement depuis :", recording_url)
    
    response = requests.get(recording_url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        filename = f"{recording.sid}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"L'enregistrement a été téléchargé et sauvegardé sous le nom : {filename}")
    else:
        print("Échec du téléchargement, code de statut :", response.status_code)
