"""
TenderWise AI - Configuration Settings
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:3001",
        "https://localhost:8080",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "tenderwise"
    POSTGRES_PASSWORD: str = "tenderwise_password"
    POSTGRES_DB: str = "tenderwise_ai"
    POSTGRES_PORT: str = "5432"
    
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # Fallback to PostgreSQL if no DATABASE_URL is set
        if values.get('POSTGRES_SERVER'):
            return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        # Default to SQLite for development
        return "sqlite:///./tenderwise_ai.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = "TenderWise AI"

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return "TenderWise AI"
        return v

    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # File Storage
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "./uploads"
    
    # Admin User
    FIRST_SUPERUSER: str = "rfp@kzahhar.com"
    FIRST_SUPERUSER_PASSWORD: str = "password123"
    
    # Application
    PROJECT_NAME: str = "TenderWise AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered RFP and Tendering Platform"
    
    # Development
    DEBUG: bool = True
    TESTING: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()