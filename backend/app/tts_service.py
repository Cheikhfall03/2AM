"""Meta MMS TTS Français — synthèse ultra-rapide (~50ms GPU) via VITS.
Utilise facebook/mms-tts-fra (modèle Meta officiel, qualité studio).
Le texte Wolof est affiché à l'écran via NLLB, l'audio est en français.
"""

import io
import torch
import soundfile as sf
from transformers import VitsModel, VitsTokenizer

HF_MODEL    = "facebook/mms-tts-fra"
SAMPLE_RATE = 16000


class WolofTTS:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = VitsTokenizer.from_pretrained(HF_MODEL)
        self.model     = VitsModel.from_pretrained(HF_MODEL).to(self.device)
        self.model.eval()
        print(f"[TTS] MMS Wolof chargé sur {self.device.type.upper()} — VITS ultra-rapide")

    @classmethod
    def get(cls) -> "WolofTTS":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def synthesize(self, text: str) -> bytes:
        """Retourne bytes WAV 16kHz mono en ~50ms sur GPU."""
        import numpy as np
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(**inputs).waveform
        wav = output.squeeze().cpu().float().numpy()
        # Normalise pour éliminer le bruit et éviter la saturation
        peak = np.max(np.abs(wav))
        if peak > 0:
            wav = wav / peak * 0.95
        buf = io.BytesIO()
        sf.write(buf, wav, samplerate=self.model.config.sampling_rate, format="WAV")
        return buf.getvalue()
