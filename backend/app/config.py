from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    MODEL_NAME: str

    EMBEDDING_MODEL: str

    UPLOAD_FOLDER: str

    CHROMA_DB: str

    USERS_DB: str = "users.db"

    RESUMES_DB: str = "resumes.db"

    # Optional LangSmith configuration (add to .env as needed)
    LANGSMITH_API_KEY: Optional[str] = None
    # Enable/disable LangSmith tracing (true/false)
    LANGSMITH_TRACING: bool = False
    # Custom LangSmith endpoint (if using private/region endpoint)
    LANGSMITH_ENDPOINT: Optional[str] = None
    # Project name to tag runs in LangSmith
    LANGSMITH_PROJECT: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()