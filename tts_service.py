import pyttsx3


class TextToSpeechService:
    def __init__(
        self,
        enabled: bool,
        rate: int,
        volume: float,
        language: str = "es",
        voice_id: str = "",
    ) -> None:
        self.enabled = enabled
        self.engine = None

        if not enabled:
            return

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", max(0.0, min(1.0, volume)))
        self._set_preferred_voice(language, voice_id)

    def _set_preferred_voice(self, language: str, voice_id: str) -> None:
        if not self.engine:
            return

        target = (language or "es").lower()
        requested_voice = (voice_id or "").strip().lower()
        voices = self.engine.getProperty("voices") or []
        if not voices:
            return

        def normalize(value: object) -> str:
            if isinstance(value, bytes):
                return value.decode("utf-8", errors="ignore").lower()
            return str(value).lower()

        preferred_id = None
        fallback_id = None

        for voice in voices:
            voice_id = normalize(getattr(voice, "id", ""))
            voice_name = normalize(getattr(voice, "name", ""))
            langs = getattr(voice, "languages", []) or []
            langs_text = " ".join(normalize(item) for item in langs)
            blob = f"{voice_id} {voice_name} {langs_text}"

            if requested_voice and requested_voice in blob:
                preferred_id = getattr(voice, "id", None)
                break

            if "spanish" in blob or "es_" in blob or "es-" in blob or " es" in blob:
                fallback_id = getattr(voice, "id", None)
                if target in blob:
                    preferred_id = getattr(voice, "id", None)
                    break

        selected = preferred_id or fallback_id
        if selected:
            self.engine.setProperty("voice", selected)

    def speak(self, text: str) -> None:
        if not self.enabled or not self.engine or not text:
            return

        self.engine.say(text)
        self.engine.runAndWait()
