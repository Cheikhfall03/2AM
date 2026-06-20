"""Traduction Français → Wolof via NLLB-200-distilled-600M (CTranslate2 int8, GPU)."""

import ctranslate2
from transformers import AutoTokenizer
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "nllb-600m-int8"
HF_MODEL  = "facebook/nllb-200-distilled-600M"


class WolofTranslator:
    _instance = None

    def __init__(self):
        device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        self.translator = ctranslate2.Translator(
            str(MODEL_DIR),
            device=device,
            inter_threads=1,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        print(f"[NMT] NLLB chargé sur {device.upper()}")

    @classmethod
    def get(cls) -> "WolofTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def translate(self, text: str, src_lang: str = "eng_Latn") -> str:
        self.tokenizer.src_lang = src_lang
        tokens = self.tokenizer.convert_ids_to_tokens(
            self.tokenizer.encode(text, add_special_tokens=True)
        )
        results = self.translator.translate_batch(
            [tokens],
            target_prefix=[["wol_Latn"]],
            beam_size=4,
        )
        ids = self.tokenizer.convert_tokens_to_ids(
            results[0].hypotheses[0][1:]
        )
        return self.tokenizer.decode(ids, skip_special_tokens=True)
