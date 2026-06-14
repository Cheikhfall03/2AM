"""Estimation monoculaire de distance via taille apparente."""

from config import REAL_HEIGHTS_M, FOCAL_LENGTH_PX


def estimate_distance(label: str, bbox_height_px: float) -> float | None:
    """Renvoie la distance estimée en mètres, ou None si la classe est inconnue."""
    real_h = REAL_HEIGHTS_M.get(label)
    if real_h is None or bbox_height_px <= 1:
        return None
    return (real_h * FOCAL_LENGTH_PX) / bbox_height_px


def horizontal_position(cx: float, frame_width: int) -> str:
    """Retourne 'à gauche', 'devant', ou 'à droite' selon la position dans le cadre."""
    third = frame_width / 3
    if cx < third:
        return "à gauche"
    if cx > 2 * third:
        return "à droite"
    return "devant"
