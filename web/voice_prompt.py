import os
import json
from typing import Dict
from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def get_voice_assistant_prompt(content: Dict) -> str:
    prompt = f"""
Vous êtes un générateur de prompt destiné à configurer un modèle d’assistance vocale professionnel. Votre mission est de créer une commande d’assistance vocale complète et détaillée, exclusivement basée sur les données fournies, sans ajouter d’éléments introductifs tels que des salutations ou des messages superflus.\n

Consignes à respecter :\n
1. Définir le rôle de l’assistant :\n
   - Agissez en tant qu’expert en configuration d’assistants vocaux.\n
   - Intégrez les informations fournies comme connaissances préalables et synthétisez-les pour produire une commande structurée.\n
2. Objectif :\n
   - Rédiger un prompt qui donne toutes les informations **(Importante)** et les services décrits dans les données suivante : **{json.dumps(content, indent=2, ensure_ascii=False)}**. \n
   - Le prompt généré doit être concis, précis et dépourvu de toute salutation ou élément de message inutile.\n
3. Adaptation et anticipation :\n
   - Incluez des instructions pour anticiper les besoins de l’utilisateur et adapter la réponse en fonction de ses vérifications et demandes.\n
   - Fournir les informations de manière concise tout en restant complet et fidèle aux données fournies.\n
4. Détail du service :\n
   - Intégrez tous les détails disponibles (informations sur les produits, horaires, options de commande, etc.) en les reformulant de façon professionnelle et structurée.\n
5. Ton et style :\n
   - Utilisez un ton professionnel, neutre et précis.\n
   - Assurez-vous que la commande d’assistance vocale reflète une expertise technique et une compréhension claire des informations fournies.\n
6. instruction a ajouter ala fin de la prompte  :\n
   - Répondez par une réponse courte.\n
   - Essayez de comprendre la question et les besoins de l’utilisateur.\n
   - Soyez précis et adaptatif dans vos réponses.\n
   - Si vous n'avez pas de réponse ou si la question n'est pas claire, demandez une clarification.\n
   - Si l'utilisateur demande quelque chose qui n'existe pas, répondez par "Je ne sais pas."\n


À partir de ces instructions, générez un prompt final qui sera utilisé pour configurer le modèle d’assistance vocale.\n
dans votre prompte essai de ne pas utlise ce type des carataire ``` juste donne un text complet de prompte .\n
"""
    client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
    )

    print("Réponse brute du modèle de configuration:")
    print(response.text)
    try:
        parsed_result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print("Erreur lors du chargement du JSON du modèle d'assistance:", e)
        parsed_result = {}
    return response.text
