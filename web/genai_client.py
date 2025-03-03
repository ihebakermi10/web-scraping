import os
import json
from typing import Any, Dict
from dotenv import load_dotenv
from google import genai


load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def get_genai_response(content: str) -> Dict:
    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    
    prompt = f"""
Veuillez analyser et structurer le contenu suivant d’un site web en un objet JSON bien organisé. Assurez-vous d'inclure **tous  les informations  importante**, afin de fournir une analyse exhaustive du site.

Utilisez le contenu complet du site web ci-dessous pour une **analyse approfondie** :\n
    **{content}**
"""

    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config={
            'response_mime_type': 'application/json'
        }
    )

    print("Réponse brute de GenAI:")
    print(response.text)
    
    try:
        parsed_result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print("Erreur lors du chargement du JSON :", e)
        parsed_result = {}
    
    return parsed_result
