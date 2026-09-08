"""Transcriere locală cu faster-whisper: audio -> (start, text) + limbă fixată."""
from faster_whisper import WhisperModel

MODEL_NAME = "large-v3-turbo"
ALLOWED_LANGUAGES = {"ro", "en"}


def create_model():
    return WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")


TRANSCRIBE_KWARGS = {
    "vad_filter": True,
    "vad_parameters": {"min_silence_duration_ms": 500},
    "condition_on_previous_text": False,
    "beam_size": 2,
}


def transcribe_wav(path, model, language=None):
    """Audio (orice format decodabil de PyAV) -> ([(start_seconds, text)], limbă).

    Dacă `language` e None, limba se detectează pe primele secunde și se
    fixează pentru tot fișierul; detecții în afara ALLOWED_LANGUAGES cad pe "ro".
    """
    segments_iter, info = model.transcribe(str(path), language=language, **TRANSCRIBE_KWARGS)
    lang = language or info.language
    if lang not in ALLOWED_LANGUAGES:
        lang = "ro"
        segments_iter, info = model.transcribe(str(path), language=lang, **TRANSCRIBE_KWARGS)
    results = []
    for seg in segments_iter:
        text = seg.text.strip()
        if text:
            results.append((seg.start, text))
    return results, lang
