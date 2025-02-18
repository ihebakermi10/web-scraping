
import os
import json
from urllib.parse import urlparse
from typing import List
from scraping import scrape_entire_website
from genai_client import get_genai_response
from models import Classe
from db_storage import store_results_in_db

def main():
    number_phone = input("Entrez le numéro de téléphone : ").strip()
    email = input("Entrez l'email : ").strip()
    category = input("Entrez la catégorie : ").strip()    
    start_url = input("Entrez l'URL de votre site : ").strip()
    if not start_url:
        print("Aucune URL fournie. Fin du programme.")
        return

    print(f"Démarrage du scraping sur : {start_url}")
    all_data = scrape_entire_website(start_url)

    parsed_url = urlparse(start_url)
    domain = parsed_url.netloc.replace("www.", "")

    all_text = "\n".join(all_data.values())
    print("Contenu extrait, envoi à GenAI...")

    try:
        result: [] = get_genai_response(all_text)
    except Exception as e:
        print(f"Erreur lors de l'appel à GenAI : {e}")
        return

    print("Résultat parsé (liste de Classe) :")
    for item in result:
        print(item)



    store_results_in_db(
        domain,
        all_data,
        number_phone,
        email,
        category,
        result
    )

if __name__ == "__main__":
    main()
