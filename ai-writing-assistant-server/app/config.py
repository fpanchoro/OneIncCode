import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "sk-proj-",
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
