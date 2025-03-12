import os
import json
import asyncio
import datetime
import websockets
import base64
import uuid
from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
import aiofiles  # Pour les opérations asynchrones sur fichiers

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
PORT = int(os.getenv("PORT", 5050))
SYSTEM_MESSAGE = """ 
Act as an expert voice assistant for Toulouse Burger, a handmade burger restaurant in Toulouse.
Your role is to answer questions and listen to users' needs regarding the restaurant, its menu, services, and offers.
    
Pre-existing knowledge:

*   **Restaurant:** Toulouse Burger, a handmade burger restaurant in Toulouse.
*   ... (complete system text) ...
If the user asks for something that does not exist, respond with "I don't know."
"""
VOICE = "alloy"
LOG_EVENT_TYPES = [
    "error", "response.content.done", "rate_limits.updated",
    "response.done", "input_audio_buffer.committed",
    "input_audio_buffer.speech_stopped", "input_audio_buffer.speech_started",
    "session.created"
]
SHOW_TIMING_MATH = False

app = FastAPI()

# Variables globales pour la gestion de l'appel
global_from_number = None
global_to_number = None
global_call_id = None

# Fichiers de stockage local
DATABASE_FILENAME = "Database.json"  # Pour les appels
USERS_FILENAME = "Uses.json"           # Pour les utilisateurs

# Verrous pour les accès concurrents aux fichiers JSON
db_lock = asyncio.Lock()      # Pour Database.json
users_lock = asyncio.Lock()   # Pour Uses.json

# ----- Fonctions utilitaires pour le fichier Database.json -----
async def load_database():
    print("Loading Database.json...")
    if not os.path.exists(DATABASE_FILENAME):
        print("Database file not found. Creating new Database.json.")
        async with aiofiles.open(DATABASE_FILENAME, "w") as f:
            await f.write(json.dumps({"users": {}}))
        return {"users": {}}
    async with aiofiles.open(DATABASE_FILENAME, "r") as f:
        content = await f.read()
    if not content.strip():
        print("Database file is empty. Initializing new Database.json.")
        return {"users": {}}
    print("Database loaded successfully.")
    return json.loads(content)

async def save_database(db):
    print("Saving Database.json...")
    async with aiofiles.open(DATABASE_FILENAME, "w") as f:
        await f.write(json.dumps(db, indent=4))
    print("Database saved.")

# ----- Fonctions utilitaires pour le fichier Uses.json -----
async def load_users():
    print("Loading Uses.json...")
    if not os.path.exists(USERS_FILENAME):
        print("Users file not found. Creating new Uses.json.")
        async with aiofiles.open(USERS_FILENAME, "w") as f:
            await f.write(json.dumps({"users": {}}))
        return {"users": {}}
    async with aiofiles.open(USERS_FILENAME, "r") as f:
        content = await f.read()
    if not content.strip():
        print("Users file is empty. Initializing new Uses.json.")
        return {"users": {}}
    print("Users file loaded successfully.")
    return json.loads(content)

async def save_users(users):
    print("Saving Uses.json...")
    async with aiofiles.open(USERS_FILENAME, "w") as f:
        await f.write(json.dumps(users, indent=4))
    print("Users file saved.")

# ----- Endpoint pour gérer les appels entrants -----
@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    global global_from_number, global_to_number, global_call_id
    print("Incoming call received.")
    form_data = await request.form()
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    
    print(f"Call details - From: {from_number}, To: {to_number}")
    
    global_from_number = from_number
    global_to_number = to_number
    
    call_sid = form_data.get("CallSid")
    if not call_sid:
        call_sid = f"{int(datetime.datetime.utcnow().timestamp())}"
    global_call_id = call_sid
    print(f"Call SID: {call_sid}")
    
    # Gestion du dataset des utilisateurs (Uses.json)
    async with users_lock:
        users_data = await load_users()
        if "users" not in users_data:
            users_data["users"] = {}
        # Recherche d'un utilisateur existant pour ce numéro
        user_id = None
        for uid, user in users_data["users"].items():
            if user["from_number"] == from_number:
                user_id = uid
                break
        if user_id is None:
            # Création d'un nouvel identifiant utilisateur
            user_id = str(uuid.uuid4())
            users_data["users"][user_id] = {"from_number": from_number}
            print(f"New user created: {from_number} with id {user_id}")
        await save_users(users_data)
    
    # Enregistrement de l'appel dans Database.json en utilisant l'id utilisateur
    async with db_lock:
        db = await load_database()
        if "users" not in db:
            db["users"] = {}
        if user_id not in db["users"]:
            db["users"][user_id] = {}
        if call_sid not in db["users"][user_id]:
            current_dt = datetime.datetime.utcnow()
            db["users"][user_id][call_sid] = {
                "from_number": from_number,    # Optionnel, car on a déjà l'id
                "to_number": to_number,
                "created_at": current_dt.isoformat(),
                "call_date": current_dt.date().isoformat(),
                "call_time": current_dt.time().isoformat(),
                "ended_at": None,
                "duration": None,
                "conversation_log": []
            }
            print(f"New call created for user id {user_id} with CallSid: {call_sid}")
        else:
            print(f"Call {call_sid} already exists for user id {user_id}")
        await save_database(db)
    
    host = request.url.hostname
    stream_url = f"wss://{host}/media-stream?from_number={from_number}&call_id={call_sid}"
    print(f"WebSocket URL generated: {stream_url}")
    
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=stream_url)
    response.append(connect)
    print("Returning Twilio response with WebSocket URL for media stream.")
    return HTMLResponse(content=str(response), media_type="application/xml")

# ----- WebSocket pour gérer le flux média et la conversation -----
@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    print("WebSocket connection initiated.")
    # On récupère from_number et call_id dans les query params ou via des variables globales
    from_number = websocket.query_params.get("from_number") or global_from_number
    call_id = websocket.query_params.get("call_id") or global_call_id
    if not from_number or not call_id:
        print("Missing 'from_number' or 'call_id' in WebSocket URL. Closing connection.")
        await websocket.close(code=1008)
        return

    print(f"WebSocket started for user {from_number} and call {call_id}")
    await websocket.accept()
    print("WebSocket connection accepted.")

    conversation_buffer = []
    print("Initialized conversation buffer.")

    stream_sid = None
    latest_media_timestamp = 0
    last_assistant_item = None
    mark_queue = []
    response_start_timestamp_twilio = None
    call_ended = False  

    try:
        print("Connecting to OpenAI WebSocket...")
        async with websockets.connect(
            "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17",
            extra_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as openai_ws:
            print("Connected to OpenAI WebSocket.")
            await initialize_session(openai_ws, system_message)
            
            async def receive_from_twilio():
                nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item, call_ended
                print("Starting task: receive_from_twilio.")
                try:
                    async for message in websocket.iter_text():
                        print("Received message from Twilio.")
                        data = json.loads(message)
                        if data["event"] == "media" and openai_ws.open:
                            latest_media_timestamp = int(data["media"]["timestamp"])
                            print("Audio chunk received from Twilio:", data["media"]["payload"])
                            conversation_buffer.append({
                                "speaker": "user",
                                "audio": data["media"]["payload"],
                                "timestamp": data["media"]["timestamp"]                                 

                            })
                            audio_append = {
                                "type": "input_audio_buffer.append",
                                "audio": data["media"]["payload"]
                            }
                            print("Sending audio chunk to OpenAI.")
                            await openai_ws.send(json.dumps(audio_append))
                        elif data["event"] == "start":
                            stream_sid = data["start"]["streamSid"]
                            print(f"Stream started with StreamSid: {stream_sid}")
                            response_start_timestamp_twilio = None
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data["event"] == "mark":
                            if mark_queue:
                                mark_queue.pop(0)
                                print("Mark removed from queue.")
                        elif data["event"] == "stop":
                            print("Hangup event received from Twilio. User ended the call.")
                            call_ended = True
                            async with users_lock:
                                users_data = await load_users()
                                user_id = None
                                for uid, user in users_data["users"].items():
                                    if user["from_number"] == from_number:
                                        user_id = uid
                                        break
                            if user_id is None:
                                print("User not found in Uses.json for from_number:", from_number)
                            else:
                                async with db_lock:
                                    db = await load_database()
                                    if ("users" in db and user_id in db["users"] 
                                            and call_id in db["users"][user_id]):
                                        call_record = db["users"][user_id][call_id]
                                        ended_at = datetime.datetime.utcnow()
                                        call_record["ended_at"] = ended_at.isoformat()
                                        created_at = datetime.datetime.fromisoformat(call_record["created_at"])
                                        duration = (ended_at - created_at).total_seconds()
                                        call_record["duration"] = duration
                                        call_record["conversation_log"] = conversation_buffer
                                        await save_database(db)
                                        print("Call record updated with end time, duration and conversation log.")
                            print("Conversation saved. Call is ended.")
                            break
                except WebSocketDisconnect:
                    print("Client disconnected in receive_from_twilio.")
                    raise
                except Exception as e:
                    print("Error in receive_from_twilio:", e)
                    raise
                print("Exiting task: receive_from_twilio.")
            
            async def send_to_twilio():
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio, call_ended
                print("Starting task: send_to_twilio.")
                try:
                    async for openai_message in openai_ws:
                        if call_ended:
                            print("Call ended flag detected in send_to_twilio, breaking loop.")
                            break
                        print("Received message from OpenAI.")
                        response = json.loads(openai_message)
                        if response["type"] in LOG_EVENT_TYPES:
                            print(f"Event received from OpenAI: {response['type']} - {response}")
                        if response.get("type") == "response.audio.delta" and "delta" in response:
                            try:
                                audio_payload = base64.b64encode(
                                    base64.b64decode(response["delta"])
                                ).decode("utf-8")
                            except Exception as e:
                                print("Error processing audio delta:", e)
                                audio_payload = response["delta"]
                            
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": audio_payload}
                            }
                            conversation_buffer.append({
                                "speaker": "ai",
                                "audio": audio_payload,
                                "timestamp": int(datetime.datetime.utcnow().timestamp() * 1000)
                            })
                            print("Sending audio chunk to Twilio.")
                            await websocket.send_json(audio_delta)
                            print("Chunk sent to Twilio.")
                            
                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                                if SHOW_TIMING_MATH:
                                    print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")
                            
                            if response.get("item_id"):
                                last_assistant_item = response["item_id"]
                                print(f"Response ID updated to: {last_assistant_item}")
                            
                            
                            
                            await send_mark(websocket, stream_sid)
                        
                        if response.get("type") == "input_audio_buffer.speech_started":
                            print("Speech started detected by OpenAI.")
                            if last_assistant_item:
                                print(f"Interrupting response with id: {last_assistant_item}")
                                await handle_speech_started_event()
                except WebSocketDisconnect:
                    print("Client disconnected in send_to_twilio.")
                    raise
                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")
                print("Exiting task: send_to_twilio.")
            
            async def handle_speech_started_event():
                nonlocal response_start_timestamp_twilio, last_assistant_item, latest_media_timestamp
                print("Handling speech interruption event.")
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if SHOW_TIMING_MATH:
                        print(f"Elapsed time for truncation: {elapsed_time} ms")
                    if last_assistant_item:
                        if SHOW_TIMING_MATH:
                            print(f"Truncating response {last_assistant_item} at {elapsed_time} ms.")
                        truncate_event = {
                            "type": "conversation.item.truncate",
                            "item_id": last_assistant_item,
                            "content_index": 0,
                            "audio_end_ms": elapsed_time
                        }
                        await openai_ws.send(json.dumps(truncate_event))
                        print("Truncate event sent to OpenAI.")
                    await websocket.send_json({
                        "event": "clear",
                        "streamSid": stream_sid
                    })
                    print("Clear message sent to Twilio.")
                    mark_queue.clear()
                    last_assistant_item = None
                    response_start_timestamp_twilio = None
            
            async def send_mark(connection, stream_sid):
                if stream_sid:
                    mark_event = {
                        "event": "mark",
                        "streamSid": stream_sid,
                        "mark": {"name": "responsePart"}
                    }
                    await connection.send_json(mark_event)
                    mark_queue.append("responsePart")
                    print("Mark sent to OpenAI and added to queue.")
            
            print("Starting asynchronous tasks: receive_from_twilio and send_to_twilio.")
            await asyncio.gather(receive_from_twilio(), send_to_twilio())
            print("Both asynchronous tasks completed.")
    except WebSocketDisconnect:
        print("Client disconnected in handle_media_stream.")
    except Exception as e:
        print("Error connecting to OpenAI WebSocket:", e)
    finally:
        if not call_ended:
            print("No hangup event received. Closing WebSocket connection.")
            try:
                await websocket.close()
                print("WebSocket closed successfully.")
            except Exception as e:
                print("Error closing WebSocket:", e)
        # Le log de conversation est sauvegardé lors de l'événement hangup.

# ----- Fonctions pour initialiser la session OpenAI -----
async def send_initial_conversation_item(openai_ws):
    print("Preparing to send initial conversation item to OpenAI.")
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Hello, I am a voice assistant powered by Twilio and OpenAI. How can I help you today?"
            }]
        }
    }
    try:
        await openai_ws.send(json.dumps(initial_conversation_item))
        await openai_ws.send(json.dumps({"type": "response.create"}))
        print("Initial conversation item sent to OpenAI.")
    except Exception as e:
        print("Error sending initial conversation item:", e)

async def initialize_session(openai_ws):
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print("Sending session update to OpenAI:", json.dumps(session_update))
    try:
        await openai_ws.send(json.dumps(session_update))
        print("OpenAI session initialized successfully.")
    except Exception as e:
        print("Error initializing OpenAI session:", e)

if __name__ == "__main__":
    import uvicorn
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
