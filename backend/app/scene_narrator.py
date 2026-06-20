"""Pipeline Florence-2 → NLLB (eng→wol) → MMS TTS avec cache LRU."""

from functools import lru_cache


@lru_cache(maxsize=256)
def translate_cached(caption_en: str) -> str:
    from app.nmt_service import WolofTranslator
    return WolofTranslator.get().translate(caption_en, src_lang="eng_Latn")


@lru_cache(maxsize=128)
def synthesize_cached(phrase_wo: str) -> bytes:
    from app.tts_service import WolofTTS
    return WolofTTS.get().synthesize(phrase_wo)


def describe_to_audio(image_bytes: bytes) -> tuple[str, str, bytes] | None:
    """
    image_bytes → Florence-2 (anglais) → NLLB (wolof) → MMS TTS (WAV)
    Retourne (caption_en, phrase_wo, audio_wav) ou None si rien détecté.
    """
    from app.florence_service import FlorenceService
    caption_en = FlorenceService.get().describe(image_bytes)
    if not caption_en:
        return None
    phrase_wo = translate_cached(caption_en)
    audio     = synthesize_cached(phrase_wo)
    return caption_en, phrase_wo, audio
