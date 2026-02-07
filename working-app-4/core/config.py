import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ENABLE_TRACE = os.getenv("ENABLE_EXECUTION_TRACE") == "true"
