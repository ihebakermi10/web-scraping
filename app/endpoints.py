from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from .twilio_handler import handle_media_stream
from .prompt_service import get_prompt_for_number  

router = APIRouter()

global_to_number = None

@router.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    global global_to_number  
    form_data = await request.form()
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    print(f"Incoming call from {from_number} to {to_number}")
    global_to_number = to_number
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    print("voici le numero", global_to_number)
    system_message = await get_prompt_for_number(global_to_number)
    await handle_media_stream(websocket, system_message)
