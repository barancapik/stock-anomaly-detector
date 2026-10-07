import os
import requests
from fastapi import HTTPException

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

def check_ollama():
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=3
        )
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail =(
                "Ollama is not running, please start it with 'ollama serve' and try again"
            )
        )