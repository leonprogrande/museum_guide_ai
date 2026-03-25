import google.generativeai as genai


class GeminiService:
    def __init__(self, api_key: str, model_name: str, system_prompt: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
        )
        # Chat mantiene el contexto automaticamente entre turnos.
        self.chat = self.model.start_chat(history=[])

    def answer(self, question: str) -> str:
        return self._send_message(question)

    def answer_with_qr_context(self, question: str, qr_data: str) -> str:
        prompt = (
            f"{question}\n\n"
            "Contexto detectado en el codigo QR de la escena:\n"
            f"{qr_data}\n\n"
            "Primero identifica si el contenido del QR necesita traduccion al espanol. "
            "Si contiene texto en otro idioma, traducelo de forma clara dentro de tu respuesta. "
            "Si es un enlace o un identificador, explica brevemente que contiene y luego responde la pregunta del visitante. "
            "Responde usando este contexto si ayuda a contestar la pregunta del visitante."
        )
        return self._send_message(prompt)

    def answer_with_image(self, question: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
        except OSError as err:
            print(f"[ERROR GEMINI] No se pudo abrir la imagen de contexto: {err}")
            return self.answer(question)

        prompt = (
            "Usa la imagen como contexto visual del entorno del visitante. "
            "Si la imagen ayuda, incorporala en tu respuesta; si no, responde normalmente.\n\n"
            f"Pregunta del visitante: {question}"
        )
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }
        return self._send_message([prompt, image_part])

    def answer_from_qr(self, qr_data: str) -> str:
        prompt = (
            "Se escaneo un codigo QR de una obra o recurso del museo. "
            "Contenido del QR:\n"
            f"{qr_data}\n\n"
            "Si el contenido incluye texto en otro idioma, traducelo al espanol antes de explicarlo. "
            "Explica al visitante que significa este QR y da contexto util y breve. "
            "Si el contenido es un enlace, menciona de forma clara que apunta a ese recurso."
        )
        return self._send_message(prompt)

    def reset_history(self) -> None:
        self.chat = self.model.start_chat(history=[])

    def _send_message(self, prompt) -> str:
        try:
            response = self.chat.send_message(prompt)
            return (response.text or "").strip()
        except Exception as err:
            print(f"[ERROR GEMINI] No se pudo obtener respuesta del modelo: {err}")
            return "Lo siento, no puedo responder en este momento."
