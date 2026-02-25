import speech_recognition as sr


class SpeechToTextService:
    def __init__(self, language: str) -> None:
        self.language = language

    def transcribe(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> str:
        try:
            return recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as err:
            print(f"[ERROR STT] No se pudo conectar al servicio STT: {err}")
            return ""
