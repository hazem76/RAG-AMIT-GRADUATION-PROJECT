"""Configuration settings for the application."""
import json
from typing import List

from pydantic_settings import BaseSettings


def parse_env_list(value: str) -> List[str]:
    """Parse comma-separated or JSON array env values into a list."""
    stripped = value.strip()
    if stripped.startswith("["):
        return json.loads(stripped)
    return [item.strip() for item in stripped.split(",") if item.strip()]


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_TITLE: str = "SupportMind AI"
    API_DESCRIPTION: str = "AI-Powered Customer Support Platform"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./supportmind.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Gemini API
    GEMINI_API_KEY: str = "AIzaSyBT25clT3GCbpiHkvJcgb1qHkYTIbV5CDk"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_data"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    ALLOWED_FILE_TYPES: str = "pdf,txt,docx"
    UPLOAD_DIR: str = "./uploads"

    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 5
    CONFIDENCE_THRESHOLD: float = 0.6

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )

    # WebSocket
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_file_types(self) -> List[str]:
        return parse_env_list(self.ALLOWED_FILE_TYPES)

    @property
    def cors_origins(self) -> List[str]:
        return parse_env_list(self.CORS_ORIGINS)

    @property
    def allowed_origins(self) -> List[str]:
        return parse_env_list(self.ALLOWED_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
