import google.generativeai as genai


class GeminiService:
    def __init__(self, api_key: str, model_name: str, system_prompt: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
        )

    def answer(self, question: str) -> str:
        response = self.model.generate_content(question)
        return (response.text or "").strip()
