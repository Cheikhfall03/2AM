"""Orchestration détection → priorisation → annonce audio."""

import time
from threading import Lock

import cv2
import numpy as np

from app.audio_registry import AudioRegistry
from app.config import ALERT_DISTANCE_M, ANNOUNCE_COOLDOWN_S, FR_LABELS
from app.detector import Detection, ObstacleDetector
from app.distance import estimate_distance, horizontal_position
from app.schemas import (
    AnnouncementOut,
    DetectResponse,
    DetectionOut,
    SceneSummaryOut,
)


class AnnounceCooldown:
    """Cooldown par session et par label."""

    def __init__(self):
        self._sessions: dict[str, dict[str, float]] = {}
        self._lock = Lock()

    def should_announce(self, session_id: str, label: str) -> bool:
        now = time.monotonic()
        with self._lock:
            session = self._sessions.setdefault(session_id, {})
            last = session.get(label, 0.0)
            if now - last < ANNOUNCE_COOLDOWN_S:
                return False
            session[label] = now
            return True


class DetectionService:
    def __init__(self, registry: AudioRegistry):
        self._registry = registry
        self._detector: ObstacleDetector | None = None
        self._cooldown = AnnounceCooldown()

    @property
    def model_loaded(self) -> bool:
        return self._detector is not None

    def ensure_model(self) -> ObstacleDetector:
        if self._detector is None:
            self._detector = ObstacleDetector()
        return self._detector

    def decode_image(self, content: bytes) -> np.ndarray:
        arr = np.frombuffer(content, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Image invalide ou format non supporté")
        return frame

    def _enrich(self, det: Detection, frame_w: int) -> DetectionOut:
        dist = estimate_distance(det.label, det.height)
        pos = horizontal_position(det.cx, frame_w)
        return DetectionOut(
            label=det.label,
            label_fr=FR_LABELS.get(det.label, det.label),
            confidence=round(det.confidence, 3),
            distance_m=round(dist, 2) if dist is not None else None,
            position=pos,
            bbox=[det.x1, det.y1, det.x2, det.y2],
        )

    def _pick_priority(self, detections: list[DetectionOut]) -> DetectionOut | None:
        best = None
        best_dist = float("inf")
        for det in detections:
            if det.distance_m is None or det.distance_m > ALERT_DISTANCE_M:
                continue
            if det.distance_m < best_dist:
                best = det
                best_dist = det.distance_m
        return best

    def _build_scene(self, detections: list[DetectionOut]) -> SceneSummaryOut:
        labels = list(dict.fromkeys(d.label for d in detections))
        descriptions = []
        for det in detections:
            phrase = self._registry.get_phrase(det.label)
            if phrase:
                desc = f"{phrase}, {det.position}"
            else:
                desc = f"{det.label_fr}, {det.position}"
            if det.distance_m is not None:
                desc += f", {det.distance_m:.1f}m"
            descriptions.append(desc)
        return SceneSummaryOut(
            object_count=len(detections),
            labels=labels,
            descriptions=descriptions,
        )

    def _build_announcement(self, det: DetectionOut) -> AnnouncementOut:
        phrase = self._registry.get_phrase(det.label) or det.label_fr
        audio_url = None
        if self._registry.get_audio_path(det.label):
            audio_url = f"/api/v1/audio/{det.label}"
        return AnnouncementOut(
            label=det.label,
            label_fr=det.label_fr,
            phrase_wolof=phrase,
            audio_url=audio_url,
            distance_m=det.distance_m,
            position=det.position,
            priority=True,
        )

    def process_frame(
        self,
        frame: np.ndarray,
        session_id: str = "default",
    ) -> DetectResponse:
        detector = self.ensure_model()
        raw = detector.detect(frame)
        enriched = [self._enrich(d, frame.shape[1]) for d in raw]
        scene = self._build_scene(enriched)

        priority = self._pick_priority(enriched)
        announcement = None
        skipped = False

        if priority:
            if self._cooldown.should_announce(session_id, priority.label):
                announcement = self._build_announcement(priority)
            else:
                skipped = True

        return DetectResponse(
            detections=enriched,
            announcement=announcement,
            scene=scene,
            skipped_cooldown=skipped,
        )

    def process_bytes(self, content: bytes, session_id: str = "default") -> DetectResponse:
        frame = self.decode_image(content)
        return self.process_frame(frame, session_id=session_id)
