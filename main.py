from assistant_core import VoiceAssistant
from audio_utils import suppress_alsa_warnings
from config import MUSEUM_SYSTEM_PROMPT, load_config
from gemini_service import GeminiService
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
    )

    assistant = VoiceAssistant(
        config=config,
        stt_service=stt_service,
        gemini_service=gemini_service,
        tts_service=tts_service,
    )
    assistant.run()


if __name__ == "__main__":
    main()
