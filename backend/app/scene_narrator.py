"""Génère une phrase française décrivant la scène + cache traductions Wolof."""

from functools import lru_cache
from app.schemas import DetectionOut

_POS = {"left": "à gauche", "center": "devant", "right": "à droite"}
_URGENCE_DIST = 1.5  # mètres


def build_scene_phrase(detections: list[DetectionOut]) -> str | None:
    """Construit une phrase courte en français décrivant la scène."""
    if not detections:
        return None

    with_dist = sorted(
        [d for d in detections if d.distance_m is not None],
        key=lambda d: d.distance_m,
    )
    without_dist = [d for d in detections if d.distance_m is None]
    sorted_dets = with_dist + without_dist

    if not sorted_dets:
        return None

    parts = []
    for det in sorted_dets[:2]:
        pos = _POS.get(det.position, det.position)
        if det.distance_m is not None:
            dist = round(det.distance_m, 1)
            parts.append(f"{det.label_fr} à {dist} mètre{'s' if dist > 1 else ''} {pos}")
        else:
            parts.append(f"{det.label_fr} {pos}")

    phrase = ", ".join(parts)

    # Urgence si obstacle très proche
    closest = sorted_dets[0]
    if closest.distance_m is not None and closest.distance_m < _URGENCE_DIST:
        phrase = f"Attention, {phrase}"

    return phrase + "."


@lru_cache(maxsize=256)
def translate_cached(phrase_fr: str) -> str:
    """Traduit une phrase en Wolof avec cache LRU (évite re-traduction)."""
    from app.nmt_service import WolofTranslator
    return WolofTranslator.get().translate(phrase_fr)


@lru_cache(maxsize=128)
def synthesize_cached(phrase_wo: str) -> bytes:
    """Synthétise audio WAV Wolof avec cache LRU (évite re-synthèse)."""
    from app.tts_service import WolofTTS
    return WolofTTS.get().synthesize(phrase_wo)


def describe_to_audio(detections: list[DetectionOut]) -> tuple[str, str, bytes] | None:
    """
    Pipeline complet : détections → (phrase_fr, phrase_wo, audio_wav)
    Retourne None si aucun objet détecté.
    Cache les traductions et synthèses pour les phrases répétées.
    """
    phrase_fr = build_scene_phrase(detections)
    if not phrase_fr:
        return None

    phrase_wo = translate_cached(phrase_fr)
    audio    = synthesize_cached(phrase_wo)
    return phrase_fr, phrase_wo, audio
