from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraping import scrape_entire_website
from voice_prompt import get_voice_assistant_prompt
from storage import store_genai_result
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "nehos")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "client")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    numero: str      
    url: str

class PersonalityInput(BaseModel):
    numero: int

def to_str(item):

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

    print("Received data:", data)
    print("Received URL:", data.url)
    try:
        extracted_data = scrape_entire_website(data.url)
        print("Extracted data:", extracted_data)
        print("Data types in extracted_data:", [type(text) for text in extracted_data.values()])
        all_text = "\n".join(to_str(text) for text in extracted_data.values())
        print("Concatenated text:", repr(all_text))
    except Exception as e:
        print("Error during scraping:", e)
        raise HTTPException(status_code=500, detail="Error during scraping: " + str(e))
    
    content_result = all_text
    document = {
        "url": data.url,
        "numero": data.numero,
        "content": content_result,
        "system_message": ""  
    }
    
    try:
        store_genai_result(document)
    except Exception as e:
        print("Error inserting into the database:", e)
        raise HTTPException(status_code=500, detail="Error inserting into the database: " + str(e))
    
    return {
        "message": "Data processed and stored successfully",
        "result": content_result,
        "system_message": ""
    }

@app.post("/personality_maker")
async def create_personality_maker(data: PersonalityInput):

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    document = collection.find_one({"numero": data.numero})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found for the provided number")
    
    content = document.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="No content found in the document for the given number")
    
    try:
        system_message = get_voice_assistant_prompt(content)
    except Exception as e:
        print("Error generating system message:", e)
        raise HTTPException(status_code=500, detail="Error generating system message: " + str(e))
    
    update_result = collection.update_one({"numero": data.numero}, {"$set": {"system_message": system_message}})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update the system_message in the document")
    
    return {
        "message": "System message generated and updated successfully",
        "system_message": system_message
    }

@app.get("/")
def read_root():

    return {"message": "FastAPI backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
