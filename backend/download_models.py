"""Télécharge NLLB-200-distilled-600M et le convertit en CTranslate2 int8.
Résultat : models/nllb-600m-int8/ (~600MB au lieu de 2.4GB, 3x plus rapide).
"""

import time
from pathlib import Path

MODEL_DIR = Path("models/nllb-600m-int8")
HF_MODEL  = "facebook/nllb-200-distilled-600M"

if MODEL_DIR.exists():
    print(f"[OK] Modèle int8 déjà présent dans {MODEL_DIR}")
else:
    print("Étape 1/2 — Téléchargement NLLB-600M (~2.4GB)...")
    print("       Cela peut prendre 30-60 min selon ta connexion.")
    t = time.time()

    import ctranslate2
    converter = ctranslate2.converters.TransformersConverter(
        HF_MODEL,
        low_cpu_mem_usage=True,
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print("Étape 2/2 — Conversion int8 (5-10 min après téléchargement)...")
    converter.convert(str(MODEL_DIR), quantization="int8", force=True)

    elapsed = time.time() - t
    size_mb = sum(f.stat().st_size for f in MODEL_DIR.rglob("*") if f.is_file()) / 1e6
    print(f"\n[OK] Converti en {elapsed/60:.1f} min — taille : {size_mb:.0f}MB")
    print(f"     Sauvegardé dans : {MODEL_DIR.resolve()}")

print("\nTest rapide...")
import ctranslate2
from transformers import AutoTokenizer

translator = ctranslate2.Translator(str(MODEL_DIR), device="cuda", inter_threads=1)
tokenizer  = AutoTokenizer.from_pretrained(HF_MODEL)
tokenizer.src_lang = "fra_Latn"

text   = "Attention, personne à 1 mètre devant."
tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(text, add_special_tokens=True))
result = translator.translate_batch([tokens], target_prefix=[["wol_Latn"]], beam_size=4)
ids    = tokenizer.convert_tokens_to_ids(result[0].hypotheses[0][1:])
wolof  = tokenizer.decode(ids, skip_special_tokens=True)

print(f"FR → WO : {wolof}")
print("\n=== NLLB int8 prêt. Relance le serveur. ===")
