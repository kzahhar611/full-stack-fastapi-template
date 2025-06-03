"""
TenderWise AI - Configuration Management
Centralized configuration using Pydantic Settings
"""

import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    Field,
    PostgresDsn,
    field_validator
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    
    # URLs
    FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")
    BACKEND_URL: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    
    # CORS
    ENABLE_CORS: bool = Field(default=True, env="ENABLE_CORS")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    DATABASE_URL: str = Field(
        default="sqlite:///./tenderwise_ai.db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")
    
    # Vector Database
    VECTOR_DB_URL: str = Field(
        default="postgresql://tenderwise:password@localhost:5432/tenderwise_vectors",
        env="VECTOR_DB_URL"
    )
    
    # =============================================================================
    # AUTHENTICATION & SECURITY
    # =============================================================================
    # JWT
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OAuth2 Providers
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_ID")
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_SECRET")
    
    # LDAP (Enterprise)
    LDAP_SERVER: Optional[str] = Field(default=None, env="LDAP_SERVER")
    LDAP_USER_DN: Optional[str] = Field(default=None, env="LDAP_USER_DN")
    LDAP_BIND_DN: Optional[str] = Field(default=None, env="LDAP_BIND_DN")
    LDAP_BIND_PASSWORD: Optional[str] = Field(default=None, env="LDAP_BIND_PASSWORD")
    
    # =============================================================================
    # AI PROVIDERS CONFIGURATION
    # =============================================================================
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    OPENAI_MODEL_DEFAULT: str = Field(default="gpt-4", env="OPENAI_MODEL_DEFAULT")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL_DEFAULT: str = Field(
        default="claude-3-sonnet-20240229",
        env="ANTHROPIC_MODEL_DEFAULT"
    )
    ANTHROPIC_MAX_TOKENS: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = Field(default=None, env="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Google AI
    GOOGLE_AI_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")
    GOOGLE_AI_MODEL_DEFAULT: str = Field(default="gemini-pro", env="GOOGLE_AI_MODEL_DEFAULT")
    
    # Local AI (Ollama)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL_DEFAULT: str = Field(default="llama2", env="OLLAMA_MODEL_DEFAULT")
    
    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL_DEFAULT: str = Field(
        default="microsoft/DialoGPT-medium",
        env="HUGGINGFACE_MODEL_DEFAULT"
    )
    
    # =============================================================================
    # LLM USAGE & COST MANAGEMENT
    # =============================================================================
    ENABLE_COST_TRACKING: bool = Field(default=True, env="ENABLE_COST_TRACKING")
    MONTHLY_COST_LIMIT_USD: float = Field(default=1000.0, env="MONTHLY_COST_LIMIT_USD")
    COST_ALERT_THRESHOLD: float = Field(default=0.8, env="COST_ALERT_THRESHOLD")
    
    # Rate Limiting
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, env="RATE_LIMIT_PER_DAY")
    
    # =============================================================================
    # WORKFLOW ENGINE CONFIGURATION
    # =============================================================================
    WORKFLOW_MAX_NODES: int = Field(default=100, env="WORKFLOW_MAX_NODES")
    WORKFLOW_TIMEOUT_SECONDS: int = Field(default=300, env="WORKFLOW_TIMEOUT_SECONDS")
    WORKFLOW_RETRY_ATTEMPTS: int = Field(default=3, env="WORKFLOW_RETRY_ATTEMPTS")
    ENABLE_WORKFLOW_CACHING: bool = Field(default=True, env="ENABLE_WORKFLOW_CACHING")
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    
    # =============================================================================
    # DOCUMENT PROCESSING
    # =============================================================================
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, azure, gcp
    UPLOAD_FOLDER: str = Field(default="./uploads", env="UPLOAD_FOLDER")
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")  # Alias for UPLOAD_FOLDER
    MAX_FILE_SIZE_MB: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["pdf", "docx", "pptx", "txt", "md"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME: Optional[str] = Field(default=None, env="AWS_BUCKET_NAME")
    AWS_REGION: str = Field(default="us-west-2", env="AWS_REGION")
    
    # Document Processing
    ENABLE_OCR: bool = Field(default=True, env="ENABLE_OCR")
    OCR_LANGUAGE: str = Field(default="eng+ara", env="OCR_LANGUAGE")
    PDF_DPI: int = Field(default=300, env="PDF_DPI")
    MAX_PAGES_PER_DOCUMENT: int = Field(default=500, env="MAX_PAGES_PER_DOCUMENT")
    
    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    SMTP_SSL: bool = Field(default=False, env="SMTP_SSL")
    
    FROM_EMAIL: EmailStr = Field(default="noreply@tenderwise.ai", env="FROM_EMAIL")
    FROM_NAME: str = Field(default="TenderWise AI", env="FROM_NAME")
    SUPPORT_EMAIL: EmailStr = Field(default="support@tenderwise.ai", env="SUPPORT_EMAIL")
    
    # =============================================================================
    # MULTI-TENANCY & ORGANIZATIONS
    # =============================================================================
    DEFAULT_ORG_NAME: str = Field(default="TenderWise AI", env="DEFAULT_ORG_NAME")
    DEFAULT_ORG_CURRENCY: str = Field(default="SAR", env="DEFAULT_ORG_CURRENCY")
    DEFAULT_ORG_LANGUAGE: str = Field(default="en", env="DEFAULT_ORG_LANGUAGE")
    DEFAULT_ORG_TIMEZONE: str = Field(default="Asia/Riyadh", env="DEFAULT_ORG_TIMEZONE")
    
    MAX_ENTITIES_PER_USER: int = Field(default=5, env="MAX_ENTITIES_PER_USER")
    ENABLE_ENTITY_ISOLATION: bool = Field(default=True, env="ENABLE_ENTITY_ISOLATION")
    
    # =============================================================================
    # INTERNATIONALIZATION
    # =============================================================================
    SUPPORTED_LANGUAGES: List[str] = Field(default=["en", "ar"], env="SUPPORTED_LANGUAGES")
    DEFAULT_LANGUAGE: str = Field(default="en", env="DEFAULT_LANGUAGE")
    ENABLE_RTL_SUPPORT: bool = Field(default=True, env="ENABLE_RTL_SUPPORT")
    
    # Calendar Systems
    ENABLE_HIJRI_CALENDAR: bool = Field(default=True, env="ENABLE_HIJRI_CALENDAR")
    ENABLE_GREGORIAN_CALENDAR: bool = Field(default=True, env="ENABLE_GREGORIAN_CALENDAR")
    DEFAULT_CALENDAR_TYPE: str = Field(default="gregorian", env="DEFAULT_CALENDAR_TYPE")
    
    # Currency
    SUPPORTED_CURRENCIES: List[str] = Field(
        default=["SAR", "USD", "EUR", "GBP"],
        env="SUPPORTED_CURRENCIES"
    )
    DEFAULT_CURRENCY: str = Field(default="SAR", env="DEFAULT_CURRENCY")
    
    # =============================================================================
    # ANALYTICS & MONITORING
    # =============================================================================
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    ANALYTICS_RETENTION_DAYS: int = Field(default=90, env="ANALYTICS_RETENTION_DAYS")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_PROMETHEUS_METRICS")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Logging
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="./logs/tenderwise.log", env="LOG_FILE")
    LOG_ROTATION: str = Field(default="daily", env="LOG_ROTATION")
    LOG_RETENTION_DAYS: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    # Core Features
    ENABLE_WORKFLOW_DESIGNER: bool = Field(default=True, env="ENABLE_WORKFLOW_DESIGNER")
    ENABLE_AI_AGENTS: bool = Field(default=True, env="ENABLE_AI_AGENTS")
    ENABLE_DOCUMENT_TEMPLATES: bool = Field(default=True, env="ENABLE_DOCUMENT_TEMPLATES")
    ENABLE_PROPOSAL_GENERATION: bool = Field(default=True, env="ENABLE_PROPOSAL_GENERATION")
    
    # Advanced Features
    ENABLE_REAL_TIME_COLLABORATION: bool = Field(default=False, env="ENABLE_REAL_TIME_COLLABORATION")
    ENABLE_ADVANCED_ANALYTICS: bool = Field(default=False, env="ENABLE_ADVANCED_ANALYTICS")
    ENABLE_API_MARKETPLACE: bool = Field(default=False, env="ENABLE_API_MARKETPLACE")
    
    # Enterprise Features
    ENABLE_SSO: bool = Field(default=False, env="ENABLE_SSO")
    ENABLE_AUDIT_LOGGING: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    ENABLE_COMPLIANCE_TOOLS: bool = Field(default=False, env="ENABLE_COMPLIANCE_TOOLS")
    
    # =============================================================================
    # DEVELOPMENT & TESTING
    # =============================================================================
    RELOAD_ON_CHANGE: bool = Field(default=True, env="RELOAD_ON_CHANGE")
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=True, env="ENABLE_DEBUG_TOOLBAR")
    SHOW_SQL_QUERIES: bool = Field(default=False, env="SHOW_SQL_QUERIES")
    
    # Testing
    TEST_DATABASE_URL: Optional[str] = Field(
        default="postgresql://tenderwise:password@localhost:5432/tenderwise_ai_test",
        env="TEST_DATABASE_URL"
    )
    ENABLE_TEST_DATA: bool = Field(default=True, env="ENABLE_TEST_DATA")
    MOCK_AI_RESPONSES: bool = Field(default=False, env="MOCK_AI_RESPONSES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Global settings instance
settings = get_settings()