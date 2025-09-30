from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "GWorkspace Analyzer API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Google OAuth & Gmail API
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Service
    EMAIL_SERVICE_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@gworkspaceanalyzer.com"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""

    # Google Cloud Vision API
    GOOGLE_CLOUD_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Feature Flags
    ENABLE_OCR: bool = False
    ENABLE_WEEKLY_EMAILS: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
