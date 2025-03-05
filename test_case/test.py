from dotenv import load_dotenv
import os
from twilio.rest import Client
import requests

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

recordings = client.recordings.list(limit=1)

if not recordings:
    print("Aucun enregistrement trouvé.")
else:
    recording = recordings[0]
    print("SID de l'enregistrement :", recording.sid)
 
    recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.wav')}"
    print("Téléchargement de l'enregistrement depuis :", recording_url)
    
    response = requests.get(recording_url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        filename = f"{recording.sid}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"L'enregistrement a été telechargé et sauvegardé sous le nom : {filename}")
    else:
        print("Échec du téléchargement, code de statut :", response.status_code)
