"""
Application settings and configuration management.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "ZZP Scanner"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://scanner:scanner123@localhost:5432/scanner",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        env="REDIS_URL"
    )
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(
        default="http://localhost:9200",
        env="ELASTICSEARCH_URL"
    )
    
    # API Keys (optional)
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    LINKEDIN_API_KEY: Optional[str] = Field(default=None, env="LINKEDIN_API_KEY")
    FACEBOOK_API_KEY: Optional[str] = Field(default=None, env="FACEBOOK_API_KEY")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://localhost"],
        env="ALLOWED_ORIGINS"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Crawling Settings
    CRAWL_DELAY: float = Field(default=1.0, env="CRAWL_DELAY")
    MAX_CONCURRENT_REQUESTS: int = Field(default=16, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Geographic Settings
    TARGET_COUNTRIES: List[str] = Field(
        default=["Netherlands", "Belgium", "Luxembourg", "Germany"],
        env="TARGET_COUNTRIES"
    )
    
    # Export Settings
    EXPORT_DIR: str = Field(default="/app/exports", env="EXPORT_DIR")
    MAX_EXPORT_SIZE: int = Field(default=10000, env="MAX_EXPORT_SIZE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_database_url() -> str:
    """Get database URL from settings."""
    return get_settings().DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL from settings."""
    return get_settings().REDIS_URL


def get_elasticsearch_url() -> str:
    """Get Elasticsearch URL from settings."""
    return get_settings().ELASTICSEARCH_URL 