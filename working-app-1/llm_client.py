from langchain_community.llms import Ollama

class LLMClient:
    def __init__(self, model: str = "phi4-mini"):
        """Initialize Ollama model client"""
        self.llm = Ollama(model=model)

    def generate(self, prompt: str) -> str:
        """Generate text using Ollama"""
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            print(f"[LLM ERROR]: {e}")
            return "LLM call failed."
