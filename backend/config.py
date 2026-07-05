import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application configuration"""

    # API configuration
    app_name: str = "DocuLens AI API"
    debug: bool = Field(default=True, validation_alias="DOCULENS_DEBUG")

    # CORS configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # Database configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://doculens:password@localhost:5432/doculens"
    )

    # Connection pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Auth0 configuration
    auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
    auth0_algorithms: List[str] = ["RS256"]  # Auth0 uses RS256

    # Local demo configuration
    enable_demo_ai_fallback: bool = os.getenv("ENABLE_DEMO_AI_FALLBACK", "").lower() in {"1", "true", "yes"}

    # File upload configuration
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # Google Cloud Vision API configuration
    google_application_credentials: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        ""
    )

    # Anthropic API configuration
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Set Google Cloud credentials environment variable
if settings.google_application_credentials:
    # Convert relative path to absolute path
    credentials_path = Path(settings.google_application_credentials)
    if not credentials_path.is_absolute():
        # Relative to backend directory
        credentials_path = Path(__file__).parent / credentials_path

    # Set environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path.absolute())
