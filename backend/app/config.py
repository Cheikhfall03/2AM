"""Configuration du backend de détection d'obstacles."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_DIR = ASSETS_DIR / "audio" / "wolof"
MAPPING_FILE = ASSETS_DIR / "audio" / "mapping.json"

YOLO_MODEL = "yolo11n.pt"
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.5

FOCAL_LENGTH_PX = 600.0

REAL_HEIGHTS_M = {
    "person": 1.70,
    "bicycle": 1.10,
    "car": 1.50,
    "motorcycle": 1.20,
    "bus": 3.20,
    "truck": 3.50,
    "traffic light": 3.00,
    "stop sign": 0.75,
    "bench": 0.90,
    "cat": 0.25,
    "dog": 0.50,
    "backpack": 0.45,
    "umbrella": 0.90,
    "handbag": 0.30,
    "bottle": 0.25,
    "chair": 0.90,
    "sofa": 0.85,
    "potted plant": 0.50,
    "dining table": 0.75,
    "tv": 0.55,
    "laptop": 0.25,
    "cell phone": 0.15,
    "book": 0.22,
}

FR_LABELS = {
    "person": "personne",
    "bicycle": "vélo",
    "car": "voiture",
    "motorcycle": "moto",
    "bus": "bus",
    "truck": "camion",
    "traffic light": "feu tricolore",
    "stop sign": "panneau stop",
    "bench": "banc",
    "cat": "chat",
    "dog": "chien",
    "backpack": "sac à dos",
    "umbrella": "parapluie",
    "handbag": "sac",
    "bottle": "bouteille",
    "chair": "chaise",
    "sofa": "canapé",
    "potted plant": "plante",
    "dining table": "table",
    "tv": "écran",
    "laptop": "ordinateur",
    "cell phone": "téléphone",
    "book": "livre",
}

ALERT_DISTANCE_M = 5.0
ANNOUNCE_COOLDOWN_S = 3.0

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".m4a"}
