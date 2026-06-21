"""Traduction FR→Wolof : NLLB-600M si disponible, sinon dictionnaire intégré."""

import torch
from transformers import AutoTokenizer
from pathlib import Path

HF_MODEL  = "facebook/nllb-200-distilled-600M"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "nllb-600m-int8"
_CACHE    = Path.home() / ".cache/huggingface/hub/models--facebook--nllb-200-distilled-600M"


def _nllb_ready() -> bool:
    """Vérifie si le modèle NLLB est entièrement téléchargé en cache."""
    if MODEL_DIR.exists():
        return True
    if not _CACHE.exists():
        return False
    # Cherche un fichier model >= 2GB (poids complets)
    for blob in (_CACHE / "blobs").glob("*"):
        if blob.stat().st_size > 2_000_000_000 and not blob.name.endswith(".incomplete"):
            return True
    return False


class WolofTranslator:
    _instance = None

    def __init__(self):
        if _nllb_ready():
            self._init_nllb()
        else:
            self._init_dict()

    def _init_nllb(self):
        self.tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        if MODEL_DIR.exists():
            import ctranslate2
            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
            self._ct2 = ctranslate2.Translator(str(MODEL_DIR), device=device, inter_threads=1)
            self._hf  = None
            print(f"[NMT] NLLB CTranslate2 int8 sur {device.upper()}")
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            from transformers import AutoModelForSeq2SeqLM
            self._ct2 = None
            self._hf  = AutoModelForSeq2SeqLM.from_pretrained(
                HF_MODEL, dtype=torch.float16
            ).to(device)
            self._hf.eval()
            self._device = device
            print(f"[NMT] NLLB transformers sur {device.upper()}")
        self._use_dict = False

    def _init_dict(self):
        self._use_dict = True
        self._ct2 = None
        self._hf  = None
        print("[NMT] NLLB absent — dictionnaire Wolof intégré (prototype)")

    @classmethod
    def get(cls) -> "WolofTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def translate(self, text: str, src_lang: str = "fra_Latn") -> str:
        if self._use_dict:
            from app.wolof_dict import translate_phrase
            return translate_phrase(text)

        self.tokenizer.src_lang = src_lang
        if self._ct2:
            tokens = self.tokenizer.convert_ids_to_tokens(
                self.tokenizer.encode(text, add_special_tokens=True)
            )
            res = self._ct2.translate_batch([tokens], target_prefix=[["wol_Latn"]], beam_size=4)
            ids = self.tokenizer.convert_tokens_to_ids(res[0].hypotheses[0][1:])
            return self.tokenizer.decode(ids, skip_special_tokens=True)

        inputs = self.tokenizer(text, return_tensors="pt").to(self._device)
        tgt_id = self.tokenizer.convert_tokens_to_ids("wol_Latn")
        with torch.no_grad():
            ids = self._hf.generate(**inputs, forced_bos_token_id=tgt_id, max_new_tokens=128)
        return self.tokenizer.decode(ids[0], skip_special_tokens=True)
