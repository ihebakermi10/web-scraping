# web/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl
from .scraping import scrape_entire_website
from .genai_client import get_genai_response
from .storage import store_genai_result

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    email: str
    numero: int      
    url: str
    prompte: str

@app.post("/submit")
async def submit_form(data: InputData):
    try:
        extracted_data = scrape_entire_website(data.url)
        all_text = "\n".join(extracted_data.values())
    except Exception as e:
        print("Erreur lors du scraping:", e)
        raise HTTPException(status_code=500, detail="Erreur lors du scraping: " + str(e))
    
    try:
        content_result = get_genai_response(all_text)
    except Exception as e:
        print("Erreur lors de l'appel à GenAI:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'appel à GenAI: " + str(e))
    
    document = {
        "url": data.url,
        "email": data.email,
        "numero": data.numero,
    #    "prompte": data.prompte, je veux ajouter icii  un script qui va gere redige  une  prompte d assissantce vocal qui respoosabe de reserver et donne  des infome comme dans  genai_client.py mais un autre ficher qui responsable de gere
        "content": content_result,
    }
    
    try:
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