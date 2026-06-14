"""Estimation monoculaire de distance et position horizontale."""

from app.config import REAL_HEIGHTS_M, FOCAL_LENGTH_PX


def estimate_distance(label: str, bbox_height_px: float) -> float | None:
    real_h = REAL_HEIGHTS_M.get(label)
    if real_h is None or bbox_height_px <= 1:
        return None
    return (real_h * FOCAL_LENGTH_PX) / bbox_height_px


def horizontal_position(cx: float, frame_width: int) -> str:
    third = frame_width / 3
    if cx < third:
        return "à gauche"
    if cx > 2 * third:
        return "à droite"
    return "devant"
