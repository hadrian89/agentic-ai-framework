import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

class HuggingFaceLLM:

    def __init__(self, model="facebook/opt-1.3b"):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.client = InferenceClient(token=self.api_key)
        self.model = model

    def generate(self, prompt: str) -> str:

        result = self.client.text_generation(
            prompt,
            model=self.model,
            max_new_tokens=150,
            temperature=0.7
        )

        return result
