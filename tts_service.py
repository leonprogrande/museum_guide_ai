import os
import tempfile
import time


class TextToSpeechService:
    def __init__(
        self,
        enabled: bool,
        rate: int,
        volume: float,
        language: str = "es",
        voice_id: str = "",
        provider: str = "gtts",
    ) -> None:
        self.enabled = enabled
        self.provider = (provider or "gtts").lower()
        self.language = (language or "es").lower()
        self.voice_id = (voice_id or "").strip().lower()
        self.engine = None
        self.pygame = None

        if not enabled:
            return

        if self.provider == "gtts":
            import pygame

            self.pygame = pygame
            self.pygame.mixer.init()
            return

        import pyttsx3

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", max(0.0, min(1.0, volume)))
        self._set_preferred_voice(self.language, self.voice_id)

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
            voice_value = normalize(getattr(voice, "id", ""))
            voice_name = normalize(getattr(voice, "name", ""))
            langs = getattr(voice, "languages", []) or []
            langs_text = " ".join(normalize(item) for item in langs)
            blob = f"{voice_value} {voice_name} {langs_text}"

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

    def _speak_with_gtts(self, text: str) -> None:
        if not self.pygame:
            return

        from gtts import gTTS

        tmp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name

            gTTS(text=text, lang=self.language).save(tmp_path)
            self.pygame.mixer.music.load(tmp_path)
            self.pygame.mixer.music.play()
            while self.pygame.mixer.music.get_busy():
                time.sleep(0.05)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def speak(self, text: str) -> None:
        if not self.enabled or not text:
            return

        if self.provider == "gtts":
            self._speak_with_gtts(text)
            return

        if not self.engine:
            return
        self.engine.say(text)
        self.engine.runAndWait()
