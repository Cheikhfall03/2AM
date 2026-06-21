"""Dictionnaire français→wolof pour les labels YOLO courants.
Utilisé comme fallback si NLLB n'est pas encore téléchargé.
"""

# Labels YOLO traduits en Wolof avec genre
_DICT = {
    # Personnes
    "personne":    "nit",
    "homme":       "góor",
    "femme":       "jigéen",
    # Véhicules
    "voiture":     "woto",
    "moto":        "moto",
    "vélo":        "weelu-woto",
    "bus":         "kaara",
    "camion":      "kamiyoŋ",
    "avion":       "fànaan",
    # Mobilier
    "chaise":      "bànk",
    "canapé":      "kanapee",
    "table":       "taabël",
    "lit":         "penu",
    "bureau":      "biro",
    # Objets courants
    "téléphone":   "telefon",
    "ordinateur":  "ordinatër",
    "sac":         "saak",
    "bouteille":   "mbotël",
    "tasse":       "taas",
    "livre":       "tééré",
    "écran":       "ekraan",
    "téléviseur":  "televiziyon",
    # Nourriture
    "nourriture":  "lekk",
    "gâteau":      "gato",
    # Animaux
    "chien":       "waf",
    "chat":        "muus",
    "oiseau":      "picc",
    # Espaces
    "porte":       "biir",
    "escalier":    "eskaaliye",
    "arbre":       "garab",
}

_POS_WO = {
    "left":   "ci kanam ci bët-bi",
    "center": "ci kanam",
    "right":  "ci ngëram",
}


def translate_phrase(phrase_fr: str) -> str:
    """Traduction approximative phrase FR → Wolof via dictionnaire."""
    result = phrase_fr
    for fr, wo in _DICT.items():
        result = result.replace(fr, wo)
    # Positions
    result = result.replace("à gauche", _POS_WO["left"])
    result = result.replace("devant",   _POS_WO["center"])
    result = result.replace("à droite", _POS_WO["right"])
    result = result.replace("Attention", "Seet ak sañ-sañ")
    result = result.replace("mètre",    "meetër")
    result = result.replace("mètres",   "meetër")
    result = result.replace("à",        "ci")
    return result
