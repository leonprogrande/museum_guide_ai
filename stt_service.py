import speech_recognition as sr


class SpeechToTextService:
    def __init__(self, language: str) -> None:
        self.language = language
        self.last_error_message = ""

    def transcribe(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> str:
        self.last_error_message = ""
        try:
            return recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as err:
            self.last_error_message = (
                "No pude procesar el audio porque el servicio de voz no esta disponible en este momento."
            )
            print(f"[ERROR STT] No se pudo conectar al servicio STT: {err}")
            return ""

    def consume_last_error(self) -> str:
        message = self.last_error_message
        self.last_error_message = ""
        return message
