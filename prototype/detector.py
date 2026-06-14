"""Wrapper autour de YOLOv8 (Ultralytics) pour la détection d'obstacles."""

from dataclasses import dataclass
from ultralytics import YOLO

from config import YOLO_MODEL, CONF_THRESHOLD, IOU_THRESHOLD


@dataclass
class Detection:
    label: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2


class ObstacleDetector:
    def __init__(self, model_path: str = YOLO_MODEL):
        self.model = YOLO(model_path)
        self.names = self.model.names

    def detect(self, frame) -> list[Detection]:
        results = self.model.predict(
            frame,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False,
        )
        detections: list[Detection] = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = self.names[cls_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                detections.append(Detection(label, conf, x1, y1, x2, y2))
        return detections
