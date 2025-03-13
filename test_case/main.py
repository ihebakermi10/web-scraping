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
Agis en tant qu'expert en configuration d'assistants vocaux, utilisant les données suivantes comme base de connaissances pour structurer un prompt d'assistance vocale complet et détaillé pour le restaurant "Les Copains d'Abord":

Le restaurant "Les Copains d'Abord" est un établissement de cuisine traditionnelle du Sud-Ouest situé au 38 Rue du pont Guilhemery, 31000 TOULOUSE. Leur numéro de téléphone est le 05 67 80 57 46 et leur site web est www.lescopains.fr.  Ils sont spécialisés dans les viandes succulentes, le cassoulet et le foie gras, et offrent des salles privées pour les groupes et événements.

**Horaires:**
*   Lundi: Fermé midi et soir
*   Mardi à samedi: Ouvert
*   Dimanche: Fermé le soir, rouvre le midi à partir du 9 février 2025
*   Mercredi: Fermé le midi

**Services offerts:** Restauration sur place, Plats à emporter, Repas de groupe, Événements privés, Traiteur, Livraison via Uber Eats.

**Menus:**

*   **À la carte:**
    *   **Entrées:** Oeufs parfaits (12 €, sauce au foie gras et pleurotes), Gravlax de saumon (16 €, sa quenelle de fromage frais citronné), Foie gras de canard mi-cuit “maison” (20 €, pâte de coing, pain d’épices toasté), Cassolette de queues de gambas et noix de St Jacques (16 €, à la crème de corail d'oursin), Croustillants de confit de canard (14 €, façon nems ketchup tomates et pêche maison).
    *   **Plats:** Embeurrée de linguines à la sicilienne (26€, aux gambas, sa tuile de parmesan), Curry de lotte au lait de coco en cassole (29 €, Riz thaï parfumé), Magret de canard entier (25€, sauce forestière soufflé de pommes Agata à l'emmental doux), Fricassée de ris de veau aux pleurotes (29€), Grande Salade du Sud-Ouest (18€, jambon de magret, toast de foie gras, gésiers confits, fritons ...), Cassoulet des copains à l’ancienne (28€, au confit de canard et saucisse de Toulouse), Pluma de cochon noir ibérique (22€, sauce gorgonzola et ses garnitures), Pièce de bœuf cuit selon votre goût (25€, sauce vigneronne, soufflé de pommes Agata).
    *   **Desserts:** Crème brûlée à la cardamome verte (9€), Pavlova aux fruits rouges (10€), Tiramisu traditionnel (9€), Profiterole géante (10€, sauce chocolat), Coupe gasconne (9€, glace vanille, pruneaux à l’Armagnac, chantilly maison), Baba bouchon au rhum (9€, amarénas confites, chantilly maison), St Félicien (9€).

*   **Menu Spécial Fêtes (24/12 et 31/12):**
    *   **Entrées:** Gratin de gambas et noix de Saint-Jacques à la crème de crustacés, Foie gras de canard maison accompagné de pâte de coing et sa tuile de pain d’épices, Ravioles de queues d’écrevisses à la crème de corail d’oursin.
    *   **Plats Principaux:** Filet de bœuf sauce vigneronne, Pigeon désossé farci au foie gras et marrons, Pavé de turbot rôti au beurre blanc citronné, accompagné d’un risotto au pistil de safran.
    *   **Desserts:** Pavlova aux fruits rouges, Tiramisu traditionnel, Soufflé glacé au Grand Marnier.

*   **Menu Occitan (32 €):**
    *   **Entrée:** Salade gerseoise jambon de magret, toast de foie gras, gésiers confits, fritons ...
    *   **Plat:** Magret de canard rôti sauce forestière soufflé de pommes Agata à l'emmental doux
    *   **Dessert:** Crème brûlée à la cardamome verte

*   **Menu de la Semaine (Du 25/02 au 28/02/25):**
    *   **Formule:** Formule du midi, plat du jour 15 €, Entrée + Plat ou Plat + dessert 18 €, Entrée + Plat + Dessert 22 €
    *   **Entrée:** Feuilles de laitues croquantes en salade, saucisse de Toulouse confite, Friand maison façon grand-mère
    *   **Plat:** Filet de lieu jaune à la plancha, riz façon balinaise, Carré de porc rôti sauce poivre vert, pommes purée
    *   **Dessert:** Crêpe à la Grecque, Macaron en coque de chocolat, mangue / fruit de la passion

*   **Menu Folie d'Épicure (42.00 €):**
    *   **Entrée:** Gravlax de saumon sa Chantilly au citron jaune, Oeufs parfaits sauce pleurotes au foie gras, Croustillants de confit de canard façon nems ketchup tomate et pêche maison
    *   **Plat:** Pièce de boeuf cuit selon votre goût sauce vigneronne, soufflé de pommes Agata, Pluma de cochon noir ibérique sauce gorgonzola et ses garnitures, Curry de lotte au lait de coco en cassole riz thaï parfumé
    *   **Dessert:** UNE GOURMANDISE À CHOISIR SUR NOTRE CARTE DES DESSERTS

*   **Menu Saint-Sylvestre (80 €):**
    *   **Description:** 31 décembre - Soir
    *   **Items:** Cocktail de bienvenue, Ravioles de queues d’écrevisses, sauce homardine en mise en bouche, Pressé de foie gras de canard aux figues confites, Tartare de noix de St Jacques et crevettes bio de Madagascar aux agrumes d’Asie, Filet de bœuf en croûte, son jus court aux morilles, mousseline de panais et bavarois de carottes au beurre noisette, Pavlova Aux Fruits exotiques

*   **Menu Saint-Valentin 2022 (50 €):**
    *   **Mise en bouche:** Toast de jaune d'œuf bio, beurre demi-sel aux truffes
    *   **Entrées:** Gratin de noix de Saint-Jacques et gambas bonne-femme, Foie gras de canard mi-cuit, poire rôtie au caramel d'agrumes
    *   **Plats:** Filet mignon de veau, son jus au marsala, écrasé de pommes de terre aux truffes, fleur de brocolis, Filet de Saint-Pierre Rossini, pommes Macaire, crème de cèpes et bourgeon d'artichaud rôti
    *   **Desserts:** Le Velour Chocolat blanc, cœur passion, coulis de mangue, Le Royal Biscuit pralin, mousse chocolat, amarena confite, L'indécent Entremet au chocolat, crème au kalamansi

*   **Carte à Emporter:**
    *   **Entrées:** Terrine de lapin aux pistaches, feuilles croquantes (9€), Foie gras de canard mi-cuit (11€, sa tuile de pain d'épices et pâte de coing), Plateau lbérique (2-3p) (25€, Épaule Cebo, Chorizo Bellotta, Saucisson Bellota, Lomo Bellota, Manchego), Plateau lbérique (6-8p) (45€, Épaule Cebo, Chorizo Bellotta, Saucisson Bellota, Lomo Bellota, Manchego), Salade Fraicheur (8€, pétales de jambon cru, melon, mozzarella, basilic, épinard)
    *   **Plats:** Cassoulet à l'ancienne au confit de canard (16€), Poulet entier fermier Label Rouge 2kg min. (4 pers.) (35€, Sa farce aux éclats d’amande, pommes confites), Pavé de saumon (14€, rôti au chèvre frais, sauce miel et amandes effilées, frites de polenta), Épaule d'Agneau (origine France) (14€, à l'orientale, sauce pois-chiches, sa semoule dorée), Brochette d'onglet de veau (14€, sa compotée d'oignons de Toulouges, écrasé de pommes de terre aux herbes)
    *   **Desserts:** Tiramisù aux fraises (5€), Nems au chocolat et pistache (5€), Clafoutis aux cerises (5€)
    *   **Plats à Emporter (Détails):** Planche de charcuterie traditionnelle à Partager (2/3 pers.) (16€, Terrine de campagne, Saucisson, Saucisse sèche, Chorizo, Jambon de pays, Boudin Galabart, Saucisse de foie, condiments), Planche de charcuterie traditionnelle à Partager (4/6 pers.) (28€, Terrine de campagne, Saucisson, Saucisse sèche, Chorizo, Jambon de pays, Boudin Galabart, Saucisse de foie, condiments), Foie gras de canard mi-cuit “maison” (19€, Sa confiture d'oignons rouges au muscat), Nems de confit de canard et magret fumé (3 pièces) (15€, sauce barbecue), Cassoulet des copains à l’ancienne (20€, au confit de canard), Embeurrée de linguines à la sicilienne aux gambas (24€, sa tuile de parmesan), Embeurée de linguines Occitane (24€, magret de canard, gésiers confits, confit de canard), Baba bouchon au rhum (9€, chantilly maison), Tiramisu traditionnel (9€)

**Événements:** Soirées Étoilées (Menu spécial 24, 31 décembre et 25 décembre midi), Carte cadeau pour Noël.

**Espaces Événements Privés:** Hommage à la chanson française, Côté Verrière, Ambiance Latino / Cubaine.

**Informations supplémentaires:** Privatisation possible, Wifi, Climatisation.

**Contact:** contact@lescopains.fr

**Réseaux sociaux:** Facebook, Instagram.

**Recommandations (Guides Locaux) :** Jalis (Agence Web, www.jalis.fr), Véranda et Verrière de France (www.verandaetverrieredefrance.fr), DUO TENDRESSE (www.duotendresse.com), Cafés Bacquié (goo.gl/maps/96t7KD4nsMk), Architectura Nova, Joaillerie Chambert (goo.gl/maps/5AMuauhcanG2), Créditleaf (goo.gl/maps/NznT37usGD52), Abrir, BETTY FROMAGER AFFINEUR, Jalis (Annuaire de la gastronomie, www.guidejalis.com).

**Mots-clés:** Restaurant traditionnel, Cuisine du Sud-Ouest, Toulouse, Cassoulet, Foie gras, Repas de groupe, Événements privés, Uber Eats, Cuisine française, Sud-Ouest, Cuisine régionale, Gastronomie, Midi-Pyrénées, repas en groupe, anniversaire, réunion, séminaire, plats à emporter, repas d'affaires, cassoulet à emporter, Restaurant ouvert le Dimanche Midi, Climatisé, privatisation de restaurant.

Répondez par une réponse courte. Essayez de comprendre la question et les besoins de l’utilisateur. Soyez précis et adaptatif dans vos réponses. Si vous n'avez pas de réponse ou si la question n'est pas claire, demandez une clarification. Si l'utilisateur demande quelque chose qui n'existe pas, répondez par "Je ne sais pas."

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
            await initialize_session(openai_ws)
            
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