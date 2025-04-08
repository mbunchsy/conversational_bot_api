import os
from dataclasses import dataclass

@dataclass
class UIConfig:
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")  # El /api/v1 se añade automáticamente en APIClient
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "undefined")
    LANGUAGE: str = os.getenv("LANGUAGE", "es")