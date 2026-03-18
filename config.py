import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    wake_phrase: str
    language: str
    gemini_model: str
    gemini_api_key: str
    silence_seconds: float
    wake_phrase_limit_seconds: int
    command_timeout_seconds: int
    ambient_calibration_seconds: float
    microphone_device_index: int | None
    tts_enabled: bool
    tts_rate: int
    tts_volume: float
    tts_language: str
    tts_voice_id: str
    tts_provider: str
    qr_image_path: str
    qr_camera_index: int
    qr_timeout_seconds: float
    text_input_enabled: bool
    text_input_bypass_wake: bool


MUSEUM_SYSTEM_PROMPT = (
    "Eres un guia de museo para visitantes. "
    "Responde en espanol claro, breve y amigable. "
    "Si no sabes algo, dilo con honestidad y sugiere preguntar al personal del museo. "
    "Evita inventar datos concretos."
)


def _get_optional_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value)


def _get_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "si", "s"}:
        return True
    if normalized in {"0", "false", "no", "off", "n"}:
        return False
    return default


def load_config() -> AppConfig:
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise ValueError("Falta GEMINI_API_KEY en variables de entorno o .env")

    return AppConfig(
        wake_phrase=os.getenv("WAKE_PHRASE", "ey asistente").strip().lower(),
        language=os.getenv("STT_LANGUAGE", "es-ES").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip(),
        gemini_api_key=gemini_api_key,
        silence_seconds=float(os.getenv("SILENCE_SECONDS", "1.0")),
        wake_phrase_limit_seconds=int(os.getenv("WAKE_PHRASE_LIMIT_SECONDS", "3")),
        command_timeout_seconds=int(os.getenv("COMMAND_TIMEOUT_SECONDS", "8")),
        ambient_calibration_seconds=float(os.getenv("AMBIENT_CALIBRATION_SECONDS", "1.0")),
        microphone_device_index=_get_optional_int(os.getenv("MICROPHONE_DEVICE_INDEX")),
        tts_enabled=_get_bool(os.getenv("TTS_ENABLED"), True),
        tts_rate=int(os.getenv("TTS_RATE", "175")),
        tts_volume=float(os.getenv("TTS_VOLUME", "1.0")),
        tts_language=os.getenv("TTS_LANGUAGE", "es").strip().lower(),
        tts_voice_id=os.getenv("TTS_VOICE_ID", "").strip(),
        tts_provider=os.getenv("TTS_PROVIDER", "gtts").strip().lower(),
        qr_image_path=os.getenv("QR_IMAGE_PATH", "").strip(),
        qr_camera_index=int(os.getenv("QR_CAMERA_INDEX", "0")),
        qr_timeout_seconds=float(os.getenv("QR_TIMEOUT_SECONDS", "2")),
        text_input_enabled=_get_bool(os.getenv("TEXT_INPUT_ENABLED"), True),
        text_input_bypass_wake=_get_bool(os.getenv("TEXT_INPUT_BYPASS_WAKE"), True),
    )
