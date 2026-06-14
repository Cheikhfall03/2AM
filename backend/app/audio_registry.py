"""Gestion du mapping objets → enregistrements audio Wolof."""

import json
import shutil
from pathlib import Path
from threading import Lock

from app.config import (
    AUDIO_DIR,
    MAPPING_FILE,
    FR_LABELS,
    ALLOWED_AUDIO_EXTENSIONS,
)


class AudioRegistry:
    """Charge, met à jour et sert les enregistrements vocaux Wolof."""

    def __init__(self):
        self._lock = Lock()
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not MAPPING_FILE.exists():
            self._write_default_mapping()
        self._data = self._load()

    def _default_entries(self) -> dict:
        defaults = {
            "person": {"phrase_wolof": "Nit ci kanam", "audio_file": "person.wav"},
            "car": {"phrase_wolof": "Oto bi", "audio_file": "car.wav"},
            "bicycle": {"phrase_wolof": "Velo bi", "audio_file": "bicycle.wav"},
            "chair": {"phrase_wolof": "Siis bi", "audio_file": "chair.wav"},
            "dog": {"phrase_wolof": "Xaj bi", "audio_file": "dog.wav"},
            "bench": {"phrase_wolof": "Banq bi", "audio_file": "bench.wav"},
            "bottle": {"phrase_wolof": "Buteyu bi", "audio_file": "bottle.wav"},
            "stop sign": {"phrase_wolof": "Panoo stop", "audio_file": "stop_sign.wav"},
            "traffic light": {"phrase_wolof": "Feu bi", "audio_file": "traffic_light.wav"},
            "backpack": {"phrase_wolof": "Sac bi", "audio_file": "backpack.wav"},
        }
        entries = {}
        for label, meta in defaults.items():
            entries[label] = {
                "label_fr": FR_LABELS.get(label, label),
                "phrase_wolof": meta["phrase_wolof"],
                "audio_file": meta["audio_file"],
                "enabled": True,
            }
        return entries

    def _write_default_mapping(self) -> None:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(self._default_entries(), f, ensure_ascii=False, indent=2)

    def _load(self) -> dict:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save(self) -> None:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def reload(self) -> None:
        with self._lock:
            self._data = self._load()

    def list_mappings(self) -> list[dict]:
        with self._lock:
            result = []
            for label, entry in self._data.items():
                audio_path = self._resolve_audio_path(entry.get("audio_file"))
                result.append({
                    "label": label,
                    "label_fr": entry.get("label_fr", FR_LABELS.get(label, label)),
                    "phrase_wolof": entry.get("phrase_wolof", ""),
                    "audio_file": entry.get("audio_file"),
                    "enabled": entry.get("enabled", True),
                    "has_audio": audio_path is not None and audio_path.exists(),
                })
            return result

    def get_entry(self, label: str) -> dict | None:
        with self._lock:
            entry = self._data.get(label)
            if entry is None:
                return None
            audio_path = self._resolve_audio_path(entry.get("audio_file"))
            return {
                "label": label,
                "label_fr": entry.get("label_fr", FR_LABELS.get(label, label)),
                "phrase_wolof": entry.get("phrase_wolof", ""),
                "audio_file": entry.get("audio_file"),
                "enabled": entry.get("enabled", True),
                "has_audio": audio_path is not None and audio_path.exists(),
            }

    def update_entry(self, label: str, phrase_wolof: str | None = None, enabled: bool | None = None) -> dict:
        with self._lock:
            if label not in self._data:
                self._data[label] = {
                    "label_fr": FR_LABELS.get(label, label),
                    "phrase_wolof": "",
                    "audio_file": None,
                    "enabled": True,
                }
            entry = self._data[label]
            if phrase_wolof is not None:
                entry["phrase_wolof"] = phrase_wolof
            if enabled is not None:
                entry["enabled"] = enabled
            self._save()
        return self.get_entry(label)  # type: ignore[return-value]

    def add_label(self, label: str, phrase_wolof: str = "", label_fr: str | None = None) -> dict:
        with self._lock:
            if label not in self._data:
                self._data[label] = {
                    "label_fr": label_fr or FR_LABELS.get(label, label),
                    "phrase_wolof": phrase_wolof,
                    "audio_file": None,
                    "enabled": True,
                }
                self._save()
        return self.get_entry(label)  # type: ignore[return-value]

    def _resolve_audio_path(self, audio_file: str | None) -> Path | None:
        if not audio_file:
            return None
        return AUDIO_DIR / audio_file

    def get_audio_path(self, label: str) -> Path | None:
        with self._lock:
            entry = self._data.get(label)
            if not entry or not entry.get("enabled"):
                return None
            path = self._resolve_audio_path(entry.get("audio_file"))
            if path and path.exists():
                return path
            return None

    def get_phrase(self, label: str) -> str | None:
        entry = self.get_entry(label)
        if not entry or not entry.get("enabled"):
            return None
        phrase = entry.get("phrase_wolof", "").strip()
        return phrase or None

    def save_audio(self, label: str, filename: str, content: bytes) -> dict:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(f"Extension non supportée: {ext}")

        safe_name = f"{label.replace(' ', '_')}{ext}"
        dest = AUDIO_DIR / safe_name
        dest.write_bytes(content)

        with self._lock:
            if label not in self._data:
                self._data[label] = {
                    "label_fr": FR_LABELS.get(label, label),
                    "phrase_wolof": "",
                    "audio_file": safe_name,
                    "enabled": True,
                }
            else:
                self._data[label]["audio_file"] = safe_name
            self._save()
        return self.get_entry(label)  # type: ignore[return-value]

    def delete_audio(self, label: str) -> dict:
        with self._lock:
            entry = self._data.get(label)
            if entry and entry.get("audio_file"):
                path = self._resolve_audio_path(entry["audio_file"])
                if path and path.exists():
                    path.unlink()
                entry["audio_file"] = None
                self._save()
        return self.get_entry(label)  # type: ignore[return-value]

    def count_recorded(self) -> int:
        return sum(1 for m in self.list_mappings() if m["has_audio"])
