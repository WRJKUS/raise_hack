"""
Configuration settings for the FastAPI backend
"""

import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    app_name: str = "Leonardo's RFQ Alchemy API"
    debug: bool = False

    # API Keys
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Database Configuration
    chroma_persist_directory: str = "./chroma_proposal_db"

    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf"]
    upload_directory: str = "./uploads"

    # LLM Configuration
    default_llm_model: str = "llama-3.1-8b-instant"
    max_tokens: int = 4000
    temperature: float = 0.1

    # Vector Store Configuration
    embedding_model: str = "text-embedding-ada-002"
    vector_search_k: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get API keys from environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_directory, exist_ok=True)
        os.makedirs(self.chroma_persist_directory, exist_ok=True)


# Global settings instance
settings = Settings()
