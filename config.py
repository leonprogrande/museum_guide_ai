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


def load_config() -> AppConfig:
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise ValueError("Falta GEMINI_API_KEY en variables de entorno o .env")

    return AppConfig(
        wake_phrase=os.getenv("WAKE_PHRASE", "ey asistente").strip().lower(),
        language=os.getenv("STT_LANGUAGE", "es-ES").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        gemini_api_key=gemini_api_key,
        silence_seconds=float(os.getenv("SILENCE_SECONDS", "1.0")),
        wake_phrase_limit_seconds=int(os.getenv("WAKE_PHRASE_LIMIT_SECONDS", "3")),
        command_timeout_seconds=int(os.getenv("COMMAND_TIMEOUT_SECONDS", "8")),
        ambient_calibration_seconds=float(os.getenv("AMBIENT_CALIBRATION_SECONDS", "1.0")),
        microphone_device_index=_get_optional_int(os.getenv("MICROPHONE_DEVICE_INDEX")),
    )
