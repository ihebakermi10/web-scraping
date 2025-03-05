import os
import json
import asyncio
import datetime
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv
import aiofiles  # Pour l'écriture asynchrone

load_dotenv()

OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = (""" Agissez en tant qu'expert en assistants vocaux pour Toulouse Burger, un restaurant de burgers maison à Toulouse. Votre rôle est de répondre aux questions et d'écouter les besoins des utilisateurs concernant le restaurant, son menu, ses services et ses offres.

Connaissances préalables :

*   **Restaurant :** Toulouse Burger, restaurant de burgers maison à Toulouse.
*   **Navigation :** La Carte, Nos Formules, Le Restaurant, Livraison, Contact, Commander à emporter, Commander en livraison, Réserver.
*   **Offres Spéciales :**
    *   Burger du moment : Proposition de recette par les clients, sélection par le staff, burger offert au gagnant et portant son nom.
    *   Citation du mois : Envoi de citations par les clients (thème variable, exemple : gourmandise en Septembre), sélection par le staff, burger offert au gagnant.
*   **Cuisine :** Viande aveyronnaise, Chicken Halal.
*   **Informations Légales :** Copyright ©2024 et © 2025 Toulouse Burger, Mentions Légales, Tous droits réservés. Design : Création 31ème Avenue. Propulsé par Sydney.
*   **Description Livraison :** Livraison de burgers à Toulouse, service rapide et fiable.
*   **Expérience Restaurant :** Ingrédients frais et de haute qualité, burgers artisanaux.
*   **Processus de Commande :** Interface conviviale, large gamme de burgers (classiques, audacieux, végétariens, sans gluten, halal, saumon).
*   **Contact Livraison :** Toulouse et environs, livraison rapide.
*   **Options Alimentaires :** Carnivore, végétarien, sans gluten, halal, saumon.
*   **Référence Livraison :** Toulouse Burger est la référence pour la livraison de burgers à Toulouse.
*   **Accompagnements :** Frites maison croustillantes, boissons rafraîchissantes, desserts.
*   **Horaires de Livraison :** 19h à 21h45.
*   **Paiements :** Carte bleue, Carte Restaurant (Ticket Restaurant). Pas de chèque ni chèque vacances.
*   **Description Menu :** À emporter, sur place et livraison. Réservation possible.
*   **Catégories Menu :** Nos Menus, Nos Burgers, Nos Salades, Nos Tapas, Nos Wraps, Nos Desserts, Nos Boissons.      
*   **Composition Menu :** Burger, frites OU beignets d’oignons, sauce, boisson.
*   **Suppléments :** Steak 3,00€, Chicken 3,00€, Galette 2,50€.
*   **Prix Burger Simple :** 10€ (10,50€ en livraison).
*   **Prix Menu Simple :** 15,50€.
*   **Options Burgers :** Burger du Moment, Classique, Fred, Végétarien, Vegan, Chicken, Hot Fire, Toulouse Burger, Capitole, Marengo, Esquirol, Péri, Jaurès, Carmes, Patte d’oie.
*   **Prix Salades :** Sur place/à emporter 12,50€, livraison 13,50€.
*   **Options Salades :** Saint Pierre, Gourmande, Terroir.
*   **Prix Tapas (Sur place/à emporter & Livraison) :** Frites simples (4,00€/4,50€), Frites doubles (5,50€/6,00€), Assortiment (5,50€/6,00€), Par 10 (8,50€/9,00€), Beignets d’oignons (4,00€/4,50€).
*   **Options Tapas :** Nuggets, Chili-Cheese, Mozzarella Sticks, Bouchées Camembert, Wings, Beignets d’oignons.      
*   **Prix Wraps :** Sur place/à emporter 10€, livraison 10,50€.
*   **Options Wraps :** Fromage, Saint Aubin, Spicy, Poulet.
*   **Prix Desserts Maison (Sur place/à emporter & Livraison) :** Banoffee (4,00€/4,30€), Cookie (3,10€/3,60€), Cookie beurre de cacahuète (3,10€/3,60€), Brownie (4,00€/4,10€).
*   **Options Desserts :** Banoffee, Cookie, Cookie beurre de cacahuète, Brownie.
*   **Prix Smoothies/Milkshakes (Sur place, À emporter, Livraison) :** Smoothie fruits rouges (4,50€, 4,50€, 5,00€), Smoothie exotique (4,50€, 4,50€, 5,00€), Milkshake banane (5,00€, 5,00€, 5,50€).
*   **Prix Glaces (Sur place, À emporter, Livraison) :** Ben & Jerry's 100ml (4,00€, 4,00€, 4,50€), Ben & Jerry's 500ml (9,50€, 9,50€, 10,00€), Glaces artisanales 120ml (4,00€, 4,00€, 4,50€).
*   **Boissons :** Ice Tea, Coca, Coca Zéro, Orangina, Jus (Pomme, Orange, Fraise), Eau plate, Perrier, Bière pression artisanale, Bière en bouteille, Kumbucha.
*   **Valeurs :** Produits de qualité, Recettes Originales, Burgers 100% Toulousains.
*   **Services :** Sur place, Livraison, À emporter.
*   **Localisation :** 29 RUE GABRIEL PÉRI, 31000, TOULOUSE. Bus : L1, L8, 14, 29, 38 (Jean Jaurès, Place Bachelier). Métro : A, B (Jean Jaurès), A (Marengo).
*   **Téléphone :** 05 61 13 11 31.
*   **Horaires :** Lundi, Mardi, Mercredi, Jeudi, Vendredi, Dimanche : 12:00–14:00, 19:00–22:00.
*   **Formulaire de Contact :** Société, Nom, Prénom, E-mail, Téléphone, Objet, Votre message.
*   **Informations Légales Détaillées :** Toulouse Burger SARL, Siret, Coordonnées, Réalisation/Hébergement, etc. (Voir données fournies).
*   **Menu Simple Détails :** Sur place/à emporter (15,50€), Livraison (17€), Composition (Burger + Frites/Beignets + Boisson + Sauce). Supplément alcool, suppléments steak/chicken/galette/frites.
*   **Menu Kids Détails :** Sur place/à emporter (11,50€), Livraison (13,50€).
*   **Menu Etudiant Détails :** Sur place/à emporter (13€), Livraison (15€), Carte étudiante requise. Suppléments steak/chicken/galette/frites.
*   **Burger Simple Prix :** Sur place/à emporter (10€), Livraison (10,50€).
*   **Sauces Maison :** Roquefort, Chili, Béarnaise, Poivre, Cheddar, Mayo-Espelette, Rougail.
*   **Sauces Classiques :** Mayo, Ketchup, Barbecue.
*   **Informations Produits :** Produits frais et locaux, viande Aveyronnaise.
*   **Mentions Légales Détaillées :** Propriété intellectuelle, limitations de responsabilité, gestion des données personnelles, liens hypertextes, cookies, droit applicable, etc. (Voir données fournies).

Répondez aux questions concernant Toulouse Burger. Fournissez des informations sur le menu, les prix, les horaires, la livraison, les offres spéciales et les options de commande. Si l'utilisateur demande des informations spécifiques, donnez une réponse précise basée sur les données fournies. Anticipez les besoins de l'utilisateur en proposant des options de menu ou des servr en proposant des options de menu ou des services pertinents.

Répondez par une réponse courte.

Essayez de comprendre la question et les besoins de l’utilisateur, quelque soit sa réclamation ou son avis. Votre rôle est d'écouter et comprendre ses besoins et problèmes.

Soyez précis et adaptatif dans vos réponses.

Si vous n'avez pas de réponse ou si la question n'est pas claire, demandez une clarification. 

Si l'utilisateur demande quelque chose qui n'existe pas, répondez par "Je ne sais pas." """
)
VOICE = 'alloy'
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

async def insert_message(speaker, payload, timestamp):
    async with aiofiles.open("conversation_log.json", "a") as f: await f.write(json.dumps({"timestamp": timestamp, "speaker": speaker, "payload": payload}) + "\n")

app = FastAPI()

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    response.pause(length=1)
    response.say("Okay")
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    print("TwiML response sent for incoming call.")
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    print("=== Start of handle_media_stream ===")
    print("Client connected")
    await websocket.accept()
    print("WebSocket accepted.")

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
            print("Connection to OpenAI WebSocket established.")
            await initialize_session(openai_ws)

            async def receive_from_twilio():
                nonlocal stream_sid, latest_media_timestamp
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media' and openai_ws.open:
                            latest_media_timestamp = int(data['media']['timestamp'])
                            print("Received a Twilio audio chunk:", data['media']['payload'])
                            await insert_message("user", data['media']['payload'], data['media']['timestamp'])
                            audio_append = {
                                "type": "input_audio_buffer.append",
                                "audio": data['media']['payload']
                            }
                            await openai_ws.send(json.dumps(audio_append))
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            print(f"Incoming stream started: {stream_sid}")
                            response_start_timestamp_twilio = None
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data['event'] == 'mark':
                            if mark_queue:
                                mark_queue.pop(0)
                                print("Mark received and removed from mark_queue.")
                except WebSocketDisconnect:
                    print("Hang up detected: WebSocket connection closed (receive).")
                    raise
                except Exception as e:
                    print("Error in receive_from_twilio:", e)

            async def send_to_twilio():
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message)
                        if response['type'] in LOG_EVENT_TYPES:
                            print(f"Event received: {response['type']} - {response}")
                        if response.get('type') == 'response.audio.delta' and 'delta' in response:
                            print("Received audio chunk from OpenAI:", response['delta'])
                            await insert_message("AI", response['delta'], latest_media_timestamp)
                            audio_payload = response['delta']
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": audio_payload}
                            }
                            await websocket.send_json(audio_delta)
                            print("Chunk transmitted to Twilio.")
                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                                if SHOW_TIMING_MATH:
                                    print(f"Response started at {response_start_timestamp_twilio} ms.")
                            if response.get('item_id'):
                                last_assistant_item = response['item_id']
                                print(f"Updated item ID: {last_assistant_item}")
                            await send_mark(websocket, stream_sid)
                        if response.get('type') == 'input_audio_buffer.speech_started':
                            print("Speech started detected from OpenAI.")
                            if last_assistant_item:
                                print(f"Interrupting response {last_assistant_item}")
                                await handle_speech_started_event()
                except WebSocketDisconnect:
                    print("Hang up detected: WebSocket connection closed (send).")
                    raise
                except Exception as e:
                    print("Error in send_to_twilio:", e)

            async def handle_speech_started_event():
                nonlocal response_start_timestamp_twilio, last_assistant_item
                print("Handling speech interruption.")
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if SHOW_TIMING_MATH:
                        print(f"Elapsed time for truncation: {elapsed_time} ms.")
                    if last_assistant_item:
                        if SHOW_TIMING_MATH:
                            print(f"Truncating {last_assistant_item} at {elapsed_time} ms.")
                        truncate_event = {
                            "type": "conversation.item.truncate",
                            "item_id": last_assistant_item,
                            "content_index": 0,
                            "audio_end_ms": elapsed_time
                        }
                        await openai_ws.send(json.dumps(truncate_event))
                        print("Truncation event sent to OpenAI.")
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
                    mark_queue.append('responsePart')
                    print("Mark sent and added to mark_queue.")

            print("Starting tasks: receive_from_twilio and send_to_twilio.")
            await asyncio.gather(receive_from_twilio(), send_to_twilio())
            print("Asynchronous tasks have completed.")
    except WebSocketDisconnect:
        print("Hang up detected: the WebSocket connection was closed by the client.")
    except Exception as e:
        print("Error connecting to OpenAI WebSocket:", e)

    try:
        await websocket.close()
        print("WebSocket closed successfully.")
    except Exception as e:
        if "Unexpected ASGI message 'websocket.close'" in str(e):
            print("WebSocket already closed, no further action needed.")
        else:
            print("Error closing WebSocket:", e)
    print("=== End of handle_media_stream ===")

async def send_initial_conversation_item(openai_ws):
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
        print("Initial message sent to OpenAI.")
    except Exception as e:
        print("Error sending initial message:", e)

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
    print('Sending session update:', json.dumps(session_update))
    try:
        await openai_ws.send(json.dumps(session_update))
        print("OpenAI session initialized.")
    except Exception as e:
        print("Error initializing OpenAI session:", e)
    # Optionnel : Décommenter pour envoyer un premier message de l'assistant
    # await send_initial_conversation_item(openai_ws)

if __name__ == "__main__":
    import uvicorn
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
