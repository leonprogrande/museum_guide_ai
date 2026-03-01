import pyttsx3


class TextToSpeechService:
    def __init__(self, enabled: bool, rate: int, volume: float) -> None:
        self.enabled = enabled
        self.engine = None

        if not enabled:
            return

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", max(0.0, min(1.0, volume)))

    def speak(self, text: str) -> None:
        if not self.enabled or not self.engine or not text:
            return

        self.engine.say(text)
        self.engine.runAndWait()
