# -*- coding: utf-8 -*-

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
🔍 **Mission : Extraction des données essentielles d’un site web**  

Votre tâche est d’analyser le site ci-dessous et d’extraire **toutes les informations importantes**, en respectant sa structure et son contenu spécifique.  

## 🎯 **Objectif :**  
Récupérer **l’intégralité des données ** du site en tenant compte de son organisation et de ses spécificités. Chaque détail pertinent doit être extrait et structuré de manière claire et exploitable.  



## ✅ **Exigences de structuration :**  
- **Adaptabilité** : respecter l’organisation et le contenu propre au site  
- **Aucune information importante ne doit être oubliée**  
- **Format structuré, lisible et immédiatement exploitable**  

📝 **Contenu du site web à analyser :**  
**{content}**  
"""  


    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config={
            'response_mime_type': 'application/json'
        }
    )

    print(response.text)
    
    try:
        parsed_result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print("Erreur lors du chargement du JSON :", e)
        parsed_result = {}
    
    return parsed_result
