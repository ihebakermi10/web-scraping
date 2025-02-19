import os
import json
from urllib.parse import urlparse
from scraping import scrape_entire_website
from genai_client import get_genai_response
from storage import store_genai_result

def main():
    start_url = input("Entrez l'URL de votre site : ").strip()
    if not start_url:
        print("Aucune URL fournie. Fin du programme.")
        return

    print(f"Démarrage du scraping sur : {start_url}")
    all_data = scrape_entire_website(start_url)
    all_text = "\n".join(all_data.values())
    print("Contenu extrait, envoi à GenAI...")

    try:
        result = get_genai_response(all_text)
    except Exception as e:
        print(f"Erreur lors de l'appel à GenAI : {e}")
        return

    print("Résultat parsé (tel que généré par GenAI) :")
    print(result)

    try:
        store_genai_result(result)
    except Exception as e:
        print("Erreur lors de l'insertion dans la DB :", e)

if __name__ == "__main__":
    main()
