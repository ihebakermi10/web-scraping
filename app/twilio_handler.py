
import datetime
import json
import base64
import asyncio
import websockets
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from config import OPENAI_API_KEY, LOG_EVENT_TYPES, SHOW_TIMING_MATH
from openai_session import initialize_session
from endpoints import global_from_number, global_call_id
from endpoints import users_lock, db_lock, load_users, load_database, save_database



async def handle_media_stream(websocket: WebSocket, system_message: str):
    print("WebSocket connection initiated.")
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
