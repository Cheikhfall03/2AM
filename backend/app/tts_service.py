"""Meta MMS TTS Wolof — synthèse ultra-rapide (~50ms GPU) via VITS."""

import io
import torch
import soundfile as sf
from transformers import VitsModel, VitsTokenizer

HF_MODEL    = "facebook/mms-tts-wol"
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
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(**inputs).waveform
        wav = output.squeeze().cpu().float().numpy()
        buf = io.BytesIO()
        sf.write(buf, wav, samplerate=self.model.config.sampling_rate, format="WAV")
        return buf.getvalue()
