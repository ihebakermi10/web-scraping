import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional, Set, Dict

def get_all_links(url: str, base_url: str, visited: Set[str]) -> Set[str]:
    """
    Récupère tous les liens internes du site en évitant les doublons.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erreur {response.status_code} sur {url}")
            return set()
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(base_url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
                links.add(full_url)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête : {e}")
        return set()

def scrape_website(url: str, visited: Set[str]) -> Optional[str]:
    """
    Récupère le texte brut d'une page web.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        else:
            print(f"Erreur : Impossible de récupérer {url} (Code : {response.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête sur {url} : {e}")
        return None

def scrape_entire_website(start_url: str) -> Dict[str, str]:
    """
    Scrape toutes les pages du site à partir de l'URL de départ.
    Retourne un dictionnaire {url: texte}.
    """
    to_visit = {start_url}
    visited = set()
    extracted_data = {}
    while to_visit:
        url = to_visit.pop()
        visited.add(url)
        text = scrape_website(url, visited)
        if text:
            extracted_data[url] = text
            new_links = get_all_links(url, start_url, visited)
            to_visit.update(new_links - visited)
    return extracted_data
