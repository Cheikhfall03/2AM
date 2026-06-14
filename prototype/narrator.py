"""Génération de phrases descriptives + synthèse vocale offline.

Backend choisi automatiquement parmi: espeak-ng, espeak, spd-say.
Tous fonctionnent hors-ligne — aligné avec le principe d'autonomie complète.
"""

import shutil
import subprocess
import time
from threading import Lock

from config import FR_LABELS, ANNOUNCE_COOLDOWN_S


def describe(label: str, distance_m: float | None, position: str) -> str:
    fr_label = FR_LABELS.get(label, label)
    if distance_m is None:
        return f"Obstacle: {fr_label}, {position}."
    if distance_m < 1.0:
        return f"Attention, {fr_label} très proche, {position}."
    return f"{fr_label.capitalize()} à {distance_m:.1f} mètres, {position}."


def _detect_tts_backend(voice: str, rate: int):
    """Renvoie une fonction qui construit la commande TTS, ou None si rien dispo."""
    if shutil.which("espeak-ng"):
        return lambda txt: ["espeak-ng", "-v", voice, "-s", str(rate), txt]
    if shutil.which("espeak"):
        return lambda txt: ["espeak", "-v", voice, "-s", str(rate), txt]
    if shutil.which("spd-say"):
        # spd-say utilise -l pour la langue (fr) et -r pour le rate (-100..100).
        spd_rate = max(-100, min(100, (rate - 175) // 2))
        return lambda txt: ["spd-say", "-w", "-l", voice, "-r", str(spd_rate), txt]
    return None


class Narrator:
    """Synthèse vocale offline. Évite les annonces répétées du même obstacle."""

    def __init__(self, voice: str = "fr", rate: int = 170):
        self._build_cmd = _detect_tts_backend(voice, rate)
        if self._build_cmd is None:
            print("[narrator] Aucun moteur TTS trouvé (espeak-ng/espeak/spd-say). "
                  "Annonces affichées en console uniquement.")
        self._last_announce: dict[str, float] = {}
        self._lock = Lock()
        self._process: subprocess.Popen | None = None

    def _should_speak(self, label: str) -> bool:
        now = time.monotonic()
        with self._lock:
            last = self._last_announce.get(label, 0)
            if now - last < ANNOUNCE_COOLDOWN_S:
                return False
            self._last_announce[label] = now
            return True

    def announce(self, label: str, sentence: str) -> None:
        if not self._should_speak(label):
            return
        print(f">> {sentence}")
        if self._build_cmd is None:
            return
        # Coupe l'annonce précédente pour rester réactif en temps réel.
        if self._process and self._process.poll() is None:
            self._process.terminate()
        self._process = subprocess.Popen(
            self._build_cmd(sentence),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def shutdown(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
