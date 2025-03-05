import base64
import wave
from pydub import AudioSegment

chunks_audio1 = [
    "/////39///9/f39/f3///39/f3////9///9/////////f39/f39/f////////39/f/9///9/f3//////////f39/f39/f///f3///39//39/f3///////////////////////39/f3//f3////9/f3///////39/////f39/f/9//////////3//////f39/f39//39/f39/f39/////fw==",
    "//////////9/f3///////39//39/////////////////f///f3///39/f/9/f39/f3////9//39/f///f///////////////f3///39/f39/f3//f///f/9//39/f/9/f/9/f/9///////9/f/////////9/////f3///39///9///////////9//39/f3///////3////////9/f39/fw=="
]

chunks_audio2 = [
    "f39/f3//f39//39//////39/f3////9/f/9/f///////////f3///39/f3//f////39///9//39//////////////////////39/f/9/f///////////////f3//f/9/f39/f39/f/9/f3////////9///9/f///f///////////////f39/f////////39/f39/f39//39/f///f3//fw==",
    "f/9/f///f///////////////f/9/f39/f39/f////////////////3////////7/////f3//f/9/f39/f39/f////////3//////////////////////////f39/f39/f39/f39/f39/f///////f////3/////////+/////39//////39/f39/f3///3//////f///////////////fw==",
    "f39/f39/f39/f39/f39/f39///9/////////f////39//////////////////////////39/f///f///f////3///39/f39/f39///////9///9///9//39/f3///////////////39/f39/////////////f///f3////9///9/f39/f39///////9/////f3////9///////9/fw==",
    "f3//f3///////39/f39/f3//f/9///9//39/f/9//////////39/f39/////////f/9/f3///3//////////f3///////39/f///f///f/////////9/fn9/f39/f/////9/f3/////////+////f39/f3///3////////////////////9///9/f39//////////39/f39/f3///////w==",
    "f3//f39/f3////////9/f////39/////f/////////////9/////////////////////////f3////9///9/f39/f39//////39/f3//////////////f/////9/f///f3//////f3///////39/f39/f////3///3///////3///39/f/////////////9/f39/f39/f39/f3///////w==",
    "////f3///3//////////////f39/f39/f39/f3//f39/f3////9//////3//////////f///f/////9//39/f3///3//f/9///9/////f///////////////////////////////f3//f39/f39/f///f///f///////////f39/f////39/////f39/f3//f////39//////////////w=="
]

def merge_chunks(chunks):
    """
    Décoder chaque chunk (en base64) et concaténer les données binaires.
    """
    merged = b""
    for chunk in chunks:
        try:
            decoded = base64.b64decode(chunk)
            merged += decoded
        except Exception as e:
            print(f"Erreur lors du décodage d'un chunk : {e}")
    return merged

audio1 = merge_chunks(chunks_audio1)
audio2 = merge_chunks(chunks_audio2)
complete_audio = audio1 + audio2

initial_filename = "merged_audio.wav"
with wave.open(initial_filename, 'wb') as wf:
    wf.setnchannels(1)       
    wf.setsampwidth(1)        
    wf.setframerate(8000)      
    wf.writeframes(complete_audio)
print(f"Fichier initial sauvegardé sous '{initial_filename}'")


audio_segment = AudioSegment.from_wav(initial_filename)

audio_ameliore = audio_segment.set_sample_width(2)

improved_filename = "improved_audio.wav"
audio_ameliore.export(improved_filename, format="wav")
print(f"Fichier amélioré sauvegardé sous '{improved_filename}'")
