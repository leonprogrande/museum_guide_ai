from datetime import datetime
import queue
import sys
import threading
from time import monotonic, sleep

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

        self._typed_queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._text_thread: threading.Thread | None = None

    def run(self) -> None:
        print("Asistente iniciado.")
        print(f"Di '{self.config.wake_phrase}' para activarlo.")
        if self.config.text_input_enabled:
            print("Tambien puedes escribir tu pregunta y presionar Enter.")
            print("Si escribes mientras escucha, se enviara como alternativa al audio.")
            self._start_text_input_thread()

        while True:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=self.config.ambient_calibration_seconds,
                    )
                    print("Microfono calibrado. Escuchando...")

                    while True:
                        try:
                            if self.config.text_input_enabled and self.config.text_input_bypass_wake:
                                typed = self._pop_typed_question()
                                if typed:
                                    self._handle_question(typed)
                                    continue

                            if not self._wake_phrase_detected(source):
                                continue

                            print("\n[Wake] Activado. Habla ahora (se cierra al detectar silencio)...")
                            question = self._listen_for_command_or_text(source).strip()

                            if not question:
                                print("[INFO] No se detecto una pregunta valida.\n")
                                continue
                            self._handle_question(question)

                        except sr.WaitTimeoutError:
                            continue
            except KeyboardInterrupt:
                print("\nSaliendo...")
                self._stop_event.set()
                break
            except OSError as err:
                print(f"[ERROR] Microfono no disponible: {err}")
                print("[INFO] Reintentando abrir el microfono...")
                sleep(1.0)
                self.microphone = sr.Microphone(device_index=self.config.microphone_device_index)
            except Exception as err:
                print(f"[ERROR] {err}")
                sleep(0.5)

    def _wake_phrase_detected(self, source: sr.AudioSource) -> bool:
        # Usar timeout corto para poder atender entrada por teclado sin bloquear indefinidamente.
        wake_audio = self.recognizer.listen(
            source,
            timeout=1.0,
            phrase_time_limit=self.config.wake_phrase_limit_seconds,
        )
        wake_text = normalize_text(self.stt.transcribe(self.recognizer, wake_audio))
        return self.config.wake_phrase in wake_text

    def _start_text_input_thread(self) -> None:
        if self._text_thread is not None:
            return

        def worker() -> None:
            while not self._stop_event.is_set():
                line = sys.stdin.readline()
                if line == "":
                    print("[INFO] Entrada de texto desconectada.")
                    return
                text = line.strip()
                if text:
                    self._typed_queue.put(text)

        self._text_thread = threading.Thread(target=worker, daemon=True, name="text-input")
        self._text_thread.start()

    def _pop_typed_question(self) -> str:
        try:
            return self._typed_queue.get_nowait()
        except queue.Empty:
            return ""

    def _listen_for_command_or_text(self, source: sr.AudioSource) -> str:
        deadline = monotonic() + max(1, self.config.command_timeout_seconds)
        while monotonic() < deadline:
            typed = self._pop_typed_question()
            if typed:
                return typed

            try:
                command_audio = self.recognizer.listen(
                    source,
                    timeout=0.5,
                    phrase_time_limit=None,
                )
            except sr.WaitTimeoutError:
                continue

            question = self.stt.transcribe(self.recognizer, command_audio).strip()
            if question:
                return question
            stt_error = self.stt.consume_last_error()
            if stt_error:
                print(f"[INFO] {stt_error}")
                self.tts.speak(stt_error)
                return ""

        print("[INFO] Tiempo de escucha agotado, intenta de nuevo.")
        return ""

    def _handle_question(self, question: str) -> None:
        question_for_model = question
        qr_result = self.qr_scanner.scan()
        qr_status = self._format_qr_status(qr_result.success and bool(qr_result.data))
        if qr_result.success and qr_result.data:
            print(f"[QR] Detectado: {qr_result.data}")
            if self._is_qr_info_request(question):
                answer = self.gemini.answer_from_qr(qr_result.data)
                self._print_turn(question, answer, qr_status)
                self.tts.speak(answer)
                return

            question_for_model = self._with_qr_context(
                question=question,
                qr_data=qr_result.data,
            )
        else:
            if qr_result.error:
                print(f"[QR] {qr_result.error}")
            if self._is_qr_info_request(question):
                answer = (
                    "No detecte ningun QR en este momento. "
                    "Acerca el codigo a la camara, mejora la iluminacion y vuelve a intentar."
                )
                self._print_turn(question, answer, qr_status)
                self.tts.speak(answer)
                return

        answer = self.gemini.answer(question_for_model)
        self._print_turn(question, answer, qr_status)
        self.tts.speak(answer)

    @staticmethod
    def _is_qr_info_request(question: str) -> bool:
        q = normalize_text(question or "")
        if not q:
            return False
        if q in {"qr", "codigo qr", "código qr"}:
            return True
        keywords = (
            "informacion del qr",
            "información del qr",
            "info del qr",
            "que dice el qr",
            "qué dice el qr",
            "leer qr",
            "escanea qr",
            "escanea el qr",
            "escanea codigo",
            "escanea el codigo",
            "escanea el código",
        )
        return any(k in q for k in keywords)

    @staticmethod
    def _with_qr_context(question: str, qr_data: str) -> str:
        return (
            f"{question}\n\n"
            "Informacion de la obra actual visitada (extraida del QR):\n"
            f"{qr_data}"
        )

    @staticmethod
    def _format_qr_status(qr_detected: bool) -> str:
        if qr_detected:
            return "QR escaneado: si"
        return "QR escaneado: no"

    @staticmethod
    def _print_turn(question: str, answer: str, qr_status: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Pregunta: {question}")
        print(f"[{timestamp}] Respuesta: {answer}")
        print(f"[{timestamp}] {qr_status}\n")
