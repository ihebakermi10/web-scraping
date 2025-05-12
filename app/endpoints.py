import asyncio
import datetime
import json
import os
import uuid
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio_handler import handle_media_stream
from prompt_service import get_prompt_for_number  
import aiofiles  

router = APIRouter()

global_from_number = None
global_to_number = None
global_call_id = None

DATABASE_FILENAME = "Database.json"  
USERS_FILENAME = "Uses.json" 
db_lock = asyncio.Lock()      
users_lock = asyncio.Lock() 



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



@router.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@router.api_route("/incoming", methods=["GET", "POST"])
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
    
    async with users_lock:
        users_data = await load_users()
        if "users" not in users_data:
            users_data["users"] = {}
        user_id = None
        for uid, user in users_data["users"].items():
            if user["from_number"] == from_number:
                user_id = uid
                break
        if user_id is None:
            user_id = str(uuid.uuid4())
            users_data["users"][user_id] = {"from_number": from_number}
            print(f"New user created: {from_number} with id {user_id}")
        await save_users(users_data)
    
    async with db_lock:
        db = await load_database()
        if "users" not in db:
            db["users"] = {}
        if user_id not in db["users"]:
            db["users"][user_id] = {}
        if call_sid not in db["users"][user_id]:
            current_dt = datetime.datetime.utcnow()
            db["users"][user_id][call_sid] = {
                "from_number": from_number,    
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


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    print("voici le numero", global_to_number)
    system_message = await get_prompt_for_number(global_to_number)
    await handle_media_stream(websocket, system_message)
