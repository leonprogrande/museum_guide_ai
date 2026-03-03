from datetime import datetime

import speech_recognition as sr

from config import AppConfig
from gemini_service import GeminiService
from qr_scanner import QRScannerService
from stt_service import SpeechToTextService
from text_utils import normalize_text
from tts_service import TextToSpeechService


class VoiceAssistant:
    def __init__(
        self,
        config: AppConfig,
        stt_service: SpeechToTextService,
        gemini_service: GeminiService,
        tts_service: TextToSpeechService,
        qr_scanner: QRScannerService,
    ) -> None:
        self.config = config
        self.stt = stt_service
        self.gemini = gemini_service
        self.tts = tts_service
        self.qr_scanner = qr_scanner

        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = config.silence_seconds
        self.recognizer.dynamic_energy_threshold = True

        self.microphone = sr.Microphone(device_index=config.microphone_device_index)

    def run(self) -> None:
        print("Asistente iniciado.")
        print(f"Di '{self.config.wake_phrase}' para activarlo.")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=self.config.ambient_calibration_seconds,
            )
            print("Microfono calibrado. Escuchando...")

            while True:
                try:
                    if not self._wake_phrase_detected(source):
                        continue

                    print("\n[Wake] Activado. Habla ahora (se cierra al detectar silencio)...")

                    command_audio = self.recognizer.listen(
                        source,
                        timeout=self.config.command_timeout_seconds,
                        phrase_time_limit=None,
                    )
                    question = self.stt.transcribe(self.recognizer, command_audio).strip()

                    if not question:
                        print("[INFO] No se detecto una pregunta valida.\n")
                        continue

                    if self._is_qr_scan_command(question):
                        answer = self._handle_qr_scan()
                    else:
                        answer = self.gemini.answer(question)
                    self._print_turn(question, answer)
                    self.tts.speak(answer)

                except sr.WaitTimeoutError:
                    continue
                except KeyboardInterrupt:
                    print("\nSaliendo...")
                    break
                except Exception as err:
                    print(f"[ERROR] {err}")

    def _wake_phrase_detected(self, source: sr.AudioSource) -> bool:
        wake_audio = self.recognizer.listen(
            source,
            timeout=None,
            phrase_time_limit=self.config.wake_phrase_limit_seconds,
        )
        wake_text = normalize_text(self.stt.transcribe(self.recognizer, wake_audio))
        return self.config.wake_phrase in wake_text

    @staticmethod
    def _is_qr_scan_command(question: str) -> bool:
        normalized = normalize_text(question)
        triggers = (
            "scan qr code",
            "scan qr",
            "scanea qr",
            "escanea qr",
            "escanear qr",
            "leer qr",
            "lee qr",
        )
        return any(trigger in normalized for trigger in triggers)

    def _handle_qr_scan(self) -> str:
        print("[QR] Iniciando escaneo con camara...")
        result = self.qr_scanner.scan()
        if not result.success:
            return f"No pude escanear el codigo QR. {result.error}"
        print(f"[QR] Detectado: {result.data}")
        return self.gemini.answer_from_qr(result.data)

    @staticmethod
    def _print_turn(question: str, answer: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Pregunta: {question}")
        print(f"[{timestamp}] Respuesta: {answer}\n")
