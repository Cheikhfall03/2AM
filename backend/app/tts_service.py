"""SpeechT5 Wolof TTS — génère un WAV à partir de texte Wolof (CPU)."""

import io
import torch
import soundfile as sf
from datasets import load_dataset
from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor

HF_MODEL   = "bilalfaye/speecht5_tts-wolof-v0.2"
HF_VOCODER = "microsoft/speecht5_hifigan"
SAMPLE_RATE = 16000


class WolofTTS:
    _instance = None

    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)

        self.processor = SpeechT5Processor.from_pretrained(HF_MODEL)
        self.model = SpeechT5ForTextToSpeech.from_pretrained(HF_MODEL).to(self.device)
        self.vocoder = SpeechT5HifiGan.from_pretrained(HF_VOCODER).to(self.device)

        # Embedding de voix (locuteur de référence)
        ds = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embeddings = torch.tensor(
            ds[7306]["xvector"]
        ).unsqueeze(0).to(self.device)

        print(f"[TTS] SpeechT5 Wolof chargé sur {device.upper()}")

    @classmethod
    def get(cls) -> "WolofTTS":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def synthesize(self, text: str) -> bytes:
        """Retourne les bytes d'un fichier WAV 16kHz mono."""
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            speech = self.model.generate_speech(
                inputs["input_ids"],
                self.speaker_embeddings,
                vocoder=self.vocoder,
            )
        buf = io.BytesIO()
        sf.write(buf, speech.cpu().numpy(), samplerate=SAMPLE_RATE, format="WAV")
        return buf.getvalue()
