import uvicorn
from fastapi import FastAPI
from assistant.endpoints import router
from assistant.config import PORT

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
