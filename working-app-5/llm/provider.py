import os
from llm.grok_client import GrokLLM
from llm.ollama_client import OllamaLLM
from llm.huggingface_client import HuggingFaceLLM
from llm.gpt4all import GPT4AllLLM
from llm.openai_client import OpenAILLM
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    provider = os.getenv("LLM_CLIENT")
    print(f"Using LLM provider: {os.getenv("LLM_CLIENT")}")
    
    if provider == "openai":
        return OpenAILLM()
    if provider == "grok":
        return GrokLLM()
    if provider == "ollama":
        return OllamaLLM()
    if provider == "gptlocal":
        return GPT4AllLLM()
    if provider == "huggingface":
        return HuggingFaceLLM(model="gpt-neo-125M")
