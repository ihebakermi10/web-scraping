from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .scraping import scrape_entire_website
from .genai_client import get_genai_response
from .voice_prompt import get_voice_assistant_prompt
from .storage import store_genai_result

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mise à jour du modèle d'entrée sans le champ "prompte"
class InputData(BaseModel):
    email: str
    numero: int      
    url: str

def to_str(item):
    """
    Convertit récursivement n'importe quel objet en chaîne de caractères.
    """
    if item is None:
        return ""
    if isinstance(item, bytes):
        try:
            return item.decode('utf-8')
        except Exception:
            return str(item)
    elif isinstance(item, (list, tuple)):
        return " ".join(to_str(sub) for sub in item)
    elif isinstance(item, dict):
        return " ".join(to_str(v) for v in item.values())
    else:
        return str(item)

@app.post("/submit")
async def submit_form(data: InputData):
    print("Données reçues:", data)
    print("URL reçue:", data.url)
    try:
        # Scraping du site web
        extracted_data = scrape_entire_website(data.url)
        print("Données extraites:", extracted_data)
        print("Types dans extracted_data:", [type(text) for text in extracted_data.values()])
        all_text = "\n".join(to_str(text) for text in extracted_data.values())
        print("Texte concaténé:", repr(all_text))
    except Exception as e:
        print("Erreur lors du scraping:", e)
        raise HTTPException(status_code=500, detail="Erreur lors du scraping: " + str(e))
    
    try:
        # Analyse du contenu du site
        content_result = get_genai_response(all_text)
    except Exception as e:
        print("Erreur lors de l'appel à GenAI:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'appel à GenAI: " + str(e))
    
    try:
        # Génération de la prompt pour l'assistant vocal
        voice_prompt_result = get_voice_assistant_prompt(content_result)
    except Exception as e:
        print("Erreur lors de la génération de la prompt d'assistant vocal:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de la prompt d'assistant vocal: " + str(e))
    
    # Création du document à insérer (sans champ "prompte" venant du front)
    document = {
        "url": data.url,
        "email": data.email,
        "numero": data.numero,
        "content": content_result,
        "assistant_prompt": voice_prompt_result
    }
    
    try:
        store_genai_result(document)
    except Exception as e:
        print("Erreur lors de l'insertion dans la DB:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'insertion dans la DB: " + str(e))
    
    return {
        "message": "Données traitées et stockées avec succès",
        "result": content_result,
        "assistant_prompt": voice_prompt_result
    }

@app.get("/")
def read_root():
    return {"message": "Backend FastAPI en fonctionnement"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
