import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GrokLLM:

    def __init__(self, model="grok-beta"):
        self.model = model

        self.client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    def generate(self, prompt: str) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a UK retail banking AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content
