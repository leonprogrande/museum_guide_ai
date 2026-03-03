from assistant_core import VoiceAssistant
from audio_utils import suppress_alsa_warnings
from config import MUSEUM_SYSTEM_PROMPT, load_config
from gemini_service import GeminiService
from qr_scanner import QRScannerService
from stt_service import SpeechToTextService
from tts_service import TextToSpeechService


def main() -> None:
    suppress_alsa_warnings()

    config = load_config()
    stt_service = SpeechToTextService(language=config.language)
    gemini_service = GeminiService(
        api_key=config.gemini_api_key,
        model_name=config.gemini_model,
        system_prompt=MUSEUM_SYSTEM_PROMPT,
    )
    tts_service = TextToSpeechService(
        enabled=config.tts_enabled,
        rate=config.tts_rate,
        volume=config.tts_volume,
        language=config.tts_language,
        voice_id=config.tts_voice_id,
        provider=config.tts_provider,
    )
    qr_scanner = QRScannerService(
        camera_index=config.qr_camera_index,
        timeout_seconds=config.qr_timeout_seconds,
    )

    assistant = VoiceAssistant(
        config=config,
        stt_service=stt_service,
        gemini_service=gemini_service,
        tts_service=tts_service,
        qr_scanner=qr_scanner,
    )
    assistant.run()


if __name__ == "__main__":
    main()
