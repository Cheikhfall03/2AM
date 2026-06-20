"""BLIP image captioning — description de scène (~80ms GPU, remplace YOLO).
Utilise Salesforce/blip-image-captioning-base (224M params, natif transformers 5.x).
"""

import io
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

HF_MODEL = "Salesforce/blip-image-captioning-base"


class FlorenceService:
    """Gardé sous ce nom pour compatibilité avec scene_narrator.py."""
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = BlipProcessor.from_pretrained(HF_MODEL)
        self.model = BlipForConditionalGeneration.from_pretrained(
            HF_MODEL,
            dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
        ).to(self.device)
        self.model.eval()
        print(f"[BLIP] Chargé sur {self.device.type.upper()} — captioning ultra-rapide")

    @classmethod
    def get(cls) -> "FlorenceService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def describe(self, image_bytes: bytes) -> str | None:
        """Retourne une description anglaise de la scène en ~80ms GPU."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            ids = self.model.generate(
                **inputs,
                max_new_tokens=64,
                num_beams=3,
            )
        caption = self.processor.decode(ids[0], skip_special_tokens=True).strip()
        return caption or None
