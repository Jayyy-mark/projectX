
import os
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiChatbot:
    def __init__(self, model="gemini-2.5-flash", temperature=0):
        """Initialize the Gemini LLM with API key and settings."""
        self.model_name = model
        self.temperature = temperature
        self.api_key = os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key
        )

    def ask(self, prompt: str):
        """Send a prompt to Gemini and return the response text."""
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)


