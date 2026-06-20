"""Génère une phrase française décrivant la scène détectée."""

from app.schemas import DetectionOut


def build_scene_phrase(detections: list[DetectionOut]) -> str | None:
    """Construit une phrase courte en français pour décrire la scène."""
    if not detections:
        return None

    # Tri par distance croissante
    sorted_dets = sorted(
        [d for d in detections if d.distance_m is not None],
        key=lambda d: d.distance_m,
    )
    if not sorted_dets:
        sorted_dets = detections[:1]

    parts = []
    for det in sorted_dets[:2]:  # max 2 objets pour garder la phrase courte
        label = det.label_fr
        pos_map = {"left": "à gauche", "center": "devant", "right": "à droite"}
        pos = pos_map.get(det.position, det.position)
        if det.distance_m is not None:
            parts.append(f"{label} à {det.distance_m:.1f} mètres {pos}")
        else:
            parts.append(f"{label} {pos}")

    if not parts:
        return None

    phrase = ", ".join(parts)
    # Urgence si objet < 1.5m
    if sorted_dets[0].distance_m is not None and sorted_dets[0].distance_m < 1.5:
        phrase = "Attention, " + phrase

    return phrase + "."
