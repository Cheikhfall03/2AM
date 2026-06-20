"""API FastAPI — détection d'objets et gestion des enregistrements Wolof."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.audio_registry import AudioRegistry
from app.schemas import (
    AudioMappingEntry,
    AudioMappingUpdate,
    DetectResponse,
    HealthResponse,
)
from app.services.detection_service import DetectionService

registry = AudioRegistry()
detection_service = DetectionService(registry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    detection_service.ensure_model()  # charge YOLO en mémoire au démarrage
    yield


app = FastAPI(
    title="2AM — Assistant aveugle",
    description="Backend de détection d'objets avec annonces audio Wolof enregistrées.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    mappings = registry.list_mappings()
    return HealthResponse(
        status="ok",
        model_loaded=detection_service.model_loaded,
        mapped_objects=len(mappings),
        recorded_audio=sum(1 for m in mappings if m["has_audio"]),
    )


@app.get("/api/v1/mapping", response_model=list[AudioMappingEntry])
def list_mapping():
    return registry.list_mappings()


@app.put("/api/v1/mapping/{label}", response_model=AudioMappingEntry)
def update_mapping(label: str, body: AudioMappingUpdate):
    entry = registry.update_entry(
        label,
        phrase_wolof=body.phrase_wolof,
        enabled=body.enabled,
    )
    return entry


@app.post("/api/v1/mapping/{label}", response_model=AudioMappingEntry)
def create_mapping(label: str, phrase_wolof: str = ""):
    entry = registry.add_label(label, phrase_wolof=phrase_wolof)
    return entry


@app.post("/api/v1/audio/{label}", response_model=AudioMappingEntry)
async def upload_audio(label: str, file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Fichier audio vide")
    try:
        entry = registry.save_audio(label, file.filename or "audio.wav", content)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return entry


@app.get("/api/v1/audio/{label}")
def get_audio(label: str):
    path = registry.get_audio_path(label)
    if path is None:
        raise HTTPException(404, f"Aucun enregistrement pour '{label}'")
    media = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
    }
    return FileResponse(path, media_type=media.get(path.suffix.lower(), "audio/mpeg"))


@app.delete("/api/v1/audio/{label}", response_model=AudioMappingEntry)
def delete_audio(label: str):
    entry = registry.delete_audio(label)
    if entry is None:
        raise HTTPException(404, f"Label inconnu: {label}")
    return entry


@app.post("/api/v1/detect", response_model=DetectResponse)
async def detect_image(
    file: UploadFile = File(...),
    session_id: str = Query(default="default", description="ID session pour le cooldown"),
):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Image vide")
    try:
        return detection_service.process_bytes(content, session_id=session_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"Erreur de détection: {exc}") from exc
