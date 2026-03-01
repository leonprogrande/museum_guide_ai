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
        response = self.chat.send_message(question)
        return (response.text or "").strip()

    def reset_history(self) -> None:
        self.chat = self.model.start_chat(history=[])
