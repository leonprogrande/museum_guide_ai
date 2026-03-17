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

    def answer_from_qr(self, qr_data: str) -> str:
        prompt = (
            "Se escaneo un codigo QR de una obra o recurso del museo. "
            "Contenido del QR:\n"
            f"{qr_data}\n\n"
            "Explica al visitante que significa este QR y da contexto util y breve. "
            "Si el contenido es un enlace, menciona de forma clara que apunta a ese recurso."
        )
        return self._send_message(prompt)

    def reset_history(self) -> None:
        self.chat = self.model.start_chat(history=[])

    def _send_message(self, prompt: str) -> str:
        try:
            response = self.chat.send_message(prompt)
            return (response.text or "").strip()
        except Exception as err:
            print(f"[ERROR GEMINI] No se pudo obtener respuesta del modelo: {err}")
            return "Lo siento, no puedo responder en este momento."
