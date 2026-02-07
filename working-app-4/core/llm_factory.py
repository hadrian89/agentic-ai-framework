import os
from langchain_ollama import ChatOllama 
from langchain_openai import ChatOpenAI

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama")

    if provider == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            temperature=0,
        )

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
