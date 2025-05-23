import uvicorn
from fastapi import FastAPI
from endpoints import router
from config import PORT
from audio_endpoint import router as audio_router
app = FastAPI()
app.include_router(audio_router)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)