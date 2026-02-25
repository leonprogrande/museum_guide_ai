from assistant_core import VoiceAssistant
from config import MUSEUM_SYSTEM_PROMPT, load_config
from gemini_service import GeminiService
from stt_service import SpeechToTextService


def main() -> None:
    config = load_config()
    stt_service = SpeechToTextService(language=config.language)
    gemini_service = GeminiService(
        api_key=config.gemini_api_key,
        model_name=config.gemini_model,
        system_prompt=MUSEUM_SYSTEM_PROMPT,
    )

    assistant = VoiceAssistant(
        config=config,
        stt_service=stt_service,
        gemini_service=gemini_service,
    )
    assistant.run()


if __name__ == "__main__":
    main()
