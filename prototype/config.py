"""Configuration du prototype de détection d'obstacles."""

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

YOLO_MODEL = "yolov11n.pt"
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.5

# Focale estimée de la caméra en pixels (à calibrer pour un vrai déploiement)
FOCAL_LENGTH_PX = 600.0

# Hauteurs réelles approximatives (en mètres) par classe COCO.
# Sert au calcul monoculaire de distance: d = (H_reel * f) / H_pixels
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

# Traductions FR pour annonces vocales (le retour utilisateur est en français).
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

# Distance max d'alerte (m). Au-delà, on n'annonce pas.
ALERT_DISTANCE_M = 5.0

# Délai minimum entre deux annonces du même objet (s).
ANNOUNCE_COOLDOWN_S = 3.0
