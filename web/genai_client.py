import os
import json
from typing import Any, Dict
from google import genai



GOOGLE_API_KEY = "AIzaSyBs_CEsN0b8RnD9Wx6z5qvf_Jl0Kz3NGXk"

def get_genai_response(content: str) -> Dict:
    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    
    prompt = f"""
Veuillez analyser et structurer le contenu suivant d’un site web en un objet JSON bien organisé. Assurez-vous d'inclure tous  les informations  pertinente, afin de fournir une analyse exhaustive du site.

Utilisez le contenu complet du site web ci-dessous pour une analyse approfondie :
    {content}
"""

    response = client.models.generate_content(
        model='gemini-2.0-flash',
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
