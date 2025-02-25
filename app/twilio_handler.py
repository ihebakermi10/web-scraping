
import json
import base64
import asyncio
import websockets
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from .config import OPENAI_API_KEY, LOG_EVENT_TYPES, SHOW_TIMING_MATH
from .openai_session import initialize_session

async def handle_media_stream(websocket: WebSocket, system_message: str , mail: dict ={}):

    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        await initialize_session(openai_ws, system_message,mail)

        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        async def receive_from_twilio():
            """Recevoir les données audio de Twilio et les envoyer à l'API Realtime d'OpenAI."""
            nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Le flux entrant a commencé {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
                print("Fin du flux Twilio.")
            except WebSocketDisconnect:
                print("Client déconnecté.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Recevoir les événements de l'API Realtime d'OpenAI et renvoyer l'audio à Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio, latest_media_timestamp
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Événement reçu: {response['type']}", response)

                    if response.get('type') == 'response.done':
                        outputs = response.get('response', {}).get('output', [])
                        for item in outputs:
                            if item.get('type') == 'function_call':
                                function_name = item.get('name')
                                function_arguments = item.get('arguments')
                                call_id = item.get('call_id')
                                print(f"Appel de fonction détecté: {function_name} avec arguments {function_arguments}")
                                await handle_function_call(function_name, function_arguments, call_id)

                    elif response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp

                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    if response.get('type') == 'input_audio_buffer.speech_started':
                        print("Détection du début de la parole.")
                        if last_assistant_item:
                            print(f"Interruption de la réponse avec l'ID: {last_assistant_item}")
                            await handle_speech_started_event()



            except Exception as e:
                print(f"Erreur dans send_to_twilio: {e}")

        async def handle_function_call(function_name, function_arguments, call_id):
            if function_name in tools:
                try:
                    args = json.loads(function_arguments) if function_arguments else {}
                    result = tools[function_name](**args)
                    function_call_output_event = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": result
                        }
                    }
                    await openai_ws.send(json.dumps(function_call_output_event))
                    await openai_ws.send(json.dumps({"type": "response.create"}))
                    print(f"Résultat de la fonction '{function_name}' envoyé: {result}")
                except Exception as e:
                    print(f"Erreur lors de l'exécution de la fonction '{function_name}': {e}")
            else:
                print(f"Fonction inconnue appelée: {function_name}")

        async def handle_speech_started_event():
            """Gérer l'interruption lorsque l'utilisateur commence à parler."""
            nonlocal response_start_timestamp_twilio, last_assistant_item, latest_media_timestamp
            print("Gestion de l'événement speech_started.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(f"Calcul du temps écoulé: {elapsed_time}ms")

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(f"Tronquer l'élément ID: {last_assistant_item} à {elapsed_time}ms")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

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

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


