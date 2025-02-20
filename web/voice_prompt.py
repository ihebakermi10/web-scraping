import os
import json
from typing import Dict
from google import genai

GOOGLE_API_KEY = "AIzaSyBs_CEsN0b8RnD9Wx6z5qvf_Jl0Kz3NGXk"  

def get_voice_assistant_prompt(content: Dict) -> Dict:

    prompt = f"""
Utilisez les informations suivantes sur le restaurant pour rédiger une prompt destinée à un assistant vocal.
Votre objectif est de créer une commande d'assistance vocale claire, engageante et informative.
Cette commande doit permettre à l'assistant vocal de guider l'utilisateur pour réserver une table, 
fournir des informations sur le menu et répondre aux questions courantes sur le restaurant.
Voici les informations sur le restaurant:
{json.dumps(content, indent=2)}

Rédigez une prompt pour un assistant vocal qui:
- Invite l'utilisateur à poser des questions ou à faire une réservation.
- Donne des informations claires sur les donnes, les horaires, et les services proposés.
- Adopte un ton chaleureux, professionnel et rassurant.
"""
    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json'
        }
    )

    print("Réponse brute de Voice Assistant GenAI:")
    print(response.text)
    try:
        parsed_result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print("Erreur lors du chargement du JSON de Voice Assistant:", e)
        parsed_result = {}
    return parsed_result
