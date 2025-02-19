# web/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl
from .scraping import scrape_entire_website
from .genai_client import get_genai_response
from .storage import store_genai_result

app = FastAPI()

# Autoriser les requêtes CORS depuis le front-end (exemple : http://localhost:8001)
origins = [
    "http://localhost:8001",
    "http://127.0.0.1:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    email: EmailStr
    numero: int      # numéro de téléphone simplifié en entier
    url: HttpUrl
    prompte: str

@app.post("/submit")
async def submit_form(data: InputData):
    try:
        # Scraping du site web
        extracted_data = scrape_entire_website(data.url)
        all_text = "\n".join(extracted_data.values())
    except Exception as e:
        print("Erreur lors du scraping:", e)
        raise HTTPException(status_code=500, detail="Erreur lors du scraping: " + str(e))
    
    try:
        # Appel à GenAI
        content_result = get_genai_response(all_text)
    except Exception as e:
        print("Erreur lors de l'appel à GenAI:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'appel à GenAI: " + str(e))
    
    document = {
        "url": data.url,
        "email": data.email,
        "numero": data.numero,
        "prompte": data.prompte,
        "content": content_result,
    }
    
    try:
        # Insertion dans la base de données
        store_genai_result(document)
    except Exception as e:
        print("Erreur lors de l'insertion dans la DB:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'insertion dans la DB: " + str(e))
    
    return {"message": "Données traitées et stockées avec succès", "result": content_result}

@app.get("/")
def read_root():
    return {"message": "Backend FastAPI en fonctionnement"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
