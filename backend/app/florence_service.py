"""Florence-2-base — description de scène (~100ms GPU, remplace YOLO)."""

import io
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM

HF_MODEL = "microsoft/Florence-2-base"
TASK     = "<DETAILED_CAPTION>"


class FlorenceService:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(HF_MODEL, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL, trust_remote_code=True, torch_dtype=dtype
        ).to(self.device)
        self.model.eval()
        print(f"[Florence-2] Chargé sur {self.device.type.upper()}")

    @classmethod
    def get(cls) -> "FlorenceService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def describe(self, image_bytes: bytes) -> str | None:
        """Retourne une description anglaise de la scène en ~100ms GPU."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(text=TASK, images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=128,
                num_beams=3,
            )
        raw    = self.processor.batch_decode(ids, skip_special_tokens=False)[0]
        parsed = self.processor.post_process_generation(
            raw, task=TASK, image_size=(image.width, image.height)
        )
        caption = parsed.get(TASK, "").strip()
        return caption or None
