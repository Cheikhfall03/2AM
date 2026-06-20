"""Traduction vers Wolof via NLLB-200-distilled-600M.
Utilise CTranslate2 int8 si le modèle converti est présent, sinon transformers natif.
"""

import torch
from transformers import AutoTokenizer
from pathlib import Path

HF_MODEL  = "facebook/nllb-200-distilled-600M"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "nllb-600m-int8"


class WolofTranslator:
    _instance = None

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)

        if MODEL_DIR.exists():
            import ctranslate2
            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
            self._ct2 = ctranslate2.Translator(str(MODEL_DIR), device=device, inter_threads=1)
            self._hf  = None
            print(f"[NMT] NLLB CTranslate2 int8 sur {device.upper()}")
        else:
            from transformers import AutoModelForSeq2SeqLM
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._ct2 = None
            self._hf  = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL).to(device)
            self._hf.eval()
            self._device = device
            print(f"[NMT] NLLB transformers natif sur {device.upper()} (int8 absent)")

    @classmethod
    def get(cls) -> "WolofTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def translate(self, text: str, src_lang: str = "eng_Latn") -> str:
        self.tokenizer.src_lang = src_lang

        if self._ct2 is not None:
            tokens = self.tokenizer.convert_ids_to_tokens(
                self.tokenizer.encode(text, add_special_tokens=True)
            )
            results = self._ct2.translate_batch(
                [tokens], target_prefix=[["wol_Latn"]], beam_size=4
            )
            ids = self.tokenizer.convert_tokens_to_ids(results[0].hypotheses[0][1:])
            return self.tokenizer.decode(ids, skip_special_tokens=True)

        # Fallback transformers
        inputs = self.tokenizer(text, return_tensors="pt").to(self._device)
        tgt_lang_id = self.tokenizer.convert_tokens_to_ids("wol_Latn")
        with torch.no_grad():
            ids = self._hf.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_new_tokens=128,
            )
        return self.tokenizer.decode(ids[0], skip_special_tokens=True)
