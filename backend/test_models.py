import time, torch

print("=== Test chargement modèles ===")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"VRAM libre: {torch.cuda.mem_get_info()[0]/1e9:.1f}GB / {torch.cuda.mem_get_info()[1]/1e9:.1f}GB")
print()

print("1) YOLO11n...")
t = time.time()
from ultralytics import YOLO
YOLO("yolo11n.pt")
print(f"   OK en {time.time()-t:.1f}s")

print("2) NMT (NLLB ou dictionnaire)...")
t = time.time()
from app.nmt_service import WolofTranslator
tr = WolofTranslator()
phrase = tr.translate("Attention, personne à 1 mètre devant.")
print(f"   OK en {time.time()-t:.1f}s")
print(f"   FR → WO: {phrase}")

print("3) MMS TTS Wolof...")
t = time.time()
from app.tts_service import WolofTTS
tts = WolofTTS()
audio = tts.synthesize(phrase)
print(f"   OK en {time.time()-t:.1f}s — {len(audio)/1024:.0f}KB audio")
print()
print("=== Pipeline OK — lance: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload ===")
