"""Schémas Pydantic pour l'API."""

from pydantic import BaseModel, Field


class AudioMappingEntry(BaseModel):
    label: str
    label_fr: str
    phrase_wolof: str = ""
    audio_file: str | None = None
    enabled: bool = True
    has_audio: bool = False


class AudioMappingUpdate(BaseModel):
    phrase_wolof: str | None = None
    enabled: bool | None = None


class DetectionOut(BaseModel):
    label: str
    label_fr: str
    confidence: float
    distance_m: float | None = None
    position: str
    bbox: list[int] = Field(description="[x1, y1, x2, y2]")


class AnnouncementOut(BaseModel):
    label: str
    label_fr: str
    phrase_wolof: str
    audio_url: str | None = None
    distance_m: float | None = None
    position: str
    priority: bool = True


class SceneSummaryOut(BaseModel):
    object_count: int
    labels: list[str]
    descriptions: list[str] = Field(
        description="Courtes descriptions structurées (Wolof si mappé, sinon FR)"
    )


class DetectResponse(BaseModel):
    detections: list[DetectionOut]
    announcement: AnnouncementOut | None = None
    scene: SceneSummaryOut
    skipped_cooldown: bool = False


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    mapped_objects: int
    recorded_audio: int
