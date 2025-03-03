import os
import json
import base64
import asyncio
import datetime
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient  # Utilisation de Motor pour MongoDB

load_dotenv()

# Configuration OpenAI & Twilio
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate."
)
VOICE = 'alloy'
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB")
COLLECTION_SPEECH = os.getenv("COLLECTION_SPEECH")
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
speech_collection = db[COLLECTION_SPEECH]
print("Connexion MongoDB (Motor) établie avec succès.")

app = FastAPI()

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    response.pause(length=1)
    response.say("O.K")
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    print("Réponse TwiML envoyée pour l'appel entrant.")
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    print("=== Début de handle_media_stream ===")
    print("Client connecté")
    await websocket.accept()
    print("WebSocket accepté.")

    all_audio_chunks = []
    stream_sid = None
    latest_media_timestamp = 0
    last_assistant_item = None
    mark_queue = []
    response_start_timestamp_twilio = None

    try:
        async with websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17',
            extra_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as openai_ws:
            print("Connexion au WebSocket OpenAI établie.")
            await initialize_session(openai_ws)

            async def receive_from_twilio():
                nonlocal stream_sid, latest_media_timestamp
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media' and openai_ws.open:
                            latest_media_timestamp = int(data['media']['timestamp'])
                            print("Réception d'un chunk de Twilio :", data['media']['payload'])
                            all_audio_chunks.append(data['media']['payload'])
                            audio_append = {
                                "type": "input_audio_buffer.append",
                                "audio": data['media']['payload']
                            }
                            await openai_ws.send(json.dumps(audio_append))
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            print(f"Stream entrant démarré : {stream_sid}")
                            response_start_timestamp_twilio = None
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data['event'] == 'mark':
                            if mark_queue:
                                mark_queue.pop(0)
                                print("Mark reçu et retiré du mark_queue.")
                except WebSocketDisconnect:
                    print("Client déconnecté de Twilio (receive).")
                    if openai_ws.open:
                        await openai_ws.close()
                    raise
                except Exception as e:
                    print("Erreur dans receive_from_twilio:", e)

            async def send_to_twilio():
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message)
                        if response['type'] in LOG_EVENT_TYPES:
                            print(f"Événement reçu: {response['type']} - {response}")
                        if response.get('type') == 'response.audio.delta' and 'delta' in response:
                            print("Chunk audio reçu de OpenAI :", response['delta'])
                            all_audio_chunks.append(response['delta'])
                            try:
                                audio_payload = base64.b64encode(
                                    base64.b64decode(response['delta'])
                                ).decode('utf-8')
                            except Exception as decode_err:
                                print("Erreur lors du décodage/ré-encodage du chunk:", decode_err)
                                audio_payload = response['delta']
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": audio_payload}
                            }
                            await websocket.send_json(audio_delta)
                            print("Chunk transmis à Twilio.")
                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                                if SHOW_TIMING_MATH:
                                    print(f"Début de réponse à {response_start_timestamp_twilio} ms.")
                            if response.get('item_id'):
                                last_assistant_item = response['item_id']
                                print(f"Item ID mis à jour : {last_assistant_item}")
                            await send_mark(websocket, stream_sid)
                        if response.get('type') == 'input_audio_buffer.speech_started':
                            print("Début de parole détecté depuis OpenAI.")
                            if last_assistant_item:
                                print(f"Interruption de la réponse {last_assistant_item}")
                                await handle_speech_started_event()
                except WebSocketDisconnect:
                    print("Client déconnecté de Twilio (send).")
                    raise
                except Exception as e:
                    print("Erreur dans send_to_twilio:", e)

            async def handle_speech_started_event():
                nonlocal response_start_timestamp_twilio, last_assistant_item
                print("Gestion de l'interruption de parole.")
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if SHOW_TIMING_MATH:
                        print(f"Temps écoulé pour troncature: {elapsed_time} ms.")
                    if last_assistant_item:
                        if SHOW_TIMING_MATH:
                            print(f"Troncature de {last_assistant_item} à {elapsed_time} ms.")
                        truncate_event = {
                            "type": "conversation.item.truncate",
                            "item_id": last_assistant_item,
                            "content_index": 0,
                            "audio_end_ms": elapsed_time
                        }
                        await openai_ws.send(json.dumps(truncate_event))
                        print("Événement de troncature envoyé à OpenAI.")
                    await websocket.send_json({
                        "event": "clear",
                        "streamSid": stream_sid
                    })
                    print("Message 'clear' envoyé à Twilio.")
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
                    mark_queue.append('responsePart')
                    print("Mark envoyé et ajouté au mark_queue.")

            print("Démarrage des tâches receive_from_twilio et send_to_twilio.")
            await asyncio.gather(receive_from_twilio(), send_to_twilio())
            print("Les tâches asynchrones se sont terminées.")
    except Exception as e:
        print("Erreur lors de la connexion au WebSocket OpenAI :", e)

    print("Début du traitement final de l'audio (stockage DB uniquement)...")
 
    
    try:
        recording_time = datetime.datetime.utcnow()
        document = {
            "recording_time": recording_time,
            "all_audio_chunks": all_audio_chunks  # Pour archivage ou débogage
        }
        result = await speech_collection.insert_one(document)
        print(f"Audio enregistré dans MongoDB avec _id: {result.inserted_id}")
    except Exception as e:
        print("Erreur lors de l'insertion dans MongoDB :", e)

    try:
        await websocket.close()
        print("WebSocket fermé avec succès.")
    except Exception as e:
        if "Unexpected ASGI message 'websocket.close'" in str(e):
            print("WebSocket déjà fermé, aucune action nécessaire.")
        else:
            print("Erreur lors de la fermeture du WebSocket :", e)
    print("=== Fin de handle_media_stream ===")

async def send_initial_conversation_item(openai_ws):
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Bonjour, je suis un assistant vocal alimenté par Twilio et OpenAI. Comment puis-je vous aider ?"
            }]
        }
    }
    try:
        await openai_ws.send(json.dumps(initial_conversation_item))
        await openai_ws.send(json.dumps({"type": "response.create"}))
        print("Message initial envoyé à OpenAI.")
    except Exception as e:
        print("Erreur lors de l'envoi du message initial :", e)

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
    print('Envoi de la mise à jour de session:', json.dumps(session_update))
    try:
        await openai_ws.send(json.dumps(session_update))
        print("Session OpenAI initialisée.")
    except Exception as e:
        print("Erreur lors de l'initialisation de la session OpenAI :", e)
    # Pour que l'IA parle en premier, décommentez la ligne suivante :
    # await send_initial_conversation_item(openai_ws)

if __name__ == "__main__":
    import uvicorn
    print("Démarrage du serveur...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
