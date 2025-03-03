import json
import base64
import audioop
import wave

with open("conversation_audio.json", "r") as f:
    data = json.load(f)

conversation = data.get("conversation_audio", [])

pcm_audio_data = b""

for entry in conversation:
    audio_base64 = entry.get("audio")
    if audio_base64:
        raw_bytes = base64.b64decode(audio_base64)
        pcm_chunk = audioop.ulaw2lin(raw_bytes, 2) 
        pcm_audio_data += pcm_chunk

with wave.open("complete_conversation.wav", "wb") as wf:
    wf.setnchannels(1)        
    wf.setsampwidth(2)        
    wf.setframerate(8000)     
    wf.writeframes(pcm_audio_data)

print("Audio conversion complete. Saved as complete_conversation.wav")
