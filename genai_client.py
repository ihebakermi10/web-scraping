# genai_client.py
import os
from typing import List
from google import genai

def get_genai_response(content: str) ->[]:

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("La variable d'environnement GOOGLE_API_KEY n'est pas définie.")

    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    response = client.models.generate_content(
        model='gemini-2.0-pro-exp-02-05',
        contents=content,
        config={
            'response_mime_type': 'application/json'
        },
    )

    print("Réponse brute de GenAI:")
    print(response.text)
    return response.parsed
