"""
Configuration settings for Jung AI Backend - Railway Optimized
"""

import os
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with Railway optimization."""
    
    # Application
    app_name: str = "Jung AI Analysis System"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration (Railway optimized)
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")  # Single worker for 512MB limit
    
    # Database - Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Database connection pool (optimized for Railway)
    db_pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # Authentication
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    
    # Cost Management
    daily_budget: float = Field(default=1.00, env="DAILY_BUDGET")
    monthly_budget: float = Field(default=25.00, env="MONTHLY_BUDGET")
    
    # OpenAI Model Configuration
    default_model: str = Field(default="gpt-3.5-turbo", env="DEFAULT_MODEL")
    complex_model: str = Field(default="gpt-4-turbo-preview", env="COMPLEX_MODEL")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="jung-analysis", env="PINECONE_INDEX_NAME")
    
    # Rate Limiting (aggressive for free tier)
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=100, env="RATE_LIMIT_PER_HOUR")
    anonymous_rate_limit: int = Field(default=5, env="ANONYMOUS_RATE_LIMIT")
    
    # Session Management
    session_timeout_minutes: int = Field(default=30, env="SESSION_TIMEOUT_MINUTES")
    max_anonymous_sessions: int = Field(default=1000, env="MAX_ANONYMOUS_SESSIONS")
    
    # Memory Optimization (Railway 512MB limit)
    max_request_size: int = Field(default=1024 * 1024, env="MAX_REQUEST_SIZE")  # 1MB
    max_response_size: int = Field(default=2 * 1024 * 1024, env="MAX_RESPONSE_SIZE")  # 2MB
    
    # Caching
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    max_cache_size: int = Field(default=1000, env="MAX_CACHE_SIZE")
    
    # Jung-specific settings
    max_context_length: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    max_retrieval_chunks: int = Field(default=5, env="MAX_RETRIEVAL_CHUNKS")
    
    # CORS settings
    cors_origins: str = Field(
        default="http://localhost:3000,https://*.vercel.app",
        env="CORS_ORIGINS"
    )
    
    @validator('cors_origins')
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Health Check
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Model costs for tracking (per 1k tokens)
MODEL_COSTS = {
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "text-embedding-ada-002": {"input": 0.0001, "output": 0.0001},
}

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

def setup_logging():
    """Setup logging configuration for Railway."""
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(),  # Console output for Railway logs
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("pinecone").setLevel(logging.WARNING)
    logging.getLogger("supabase").setLevel(logging.WARNING)

def get_database_url() -> str:
    """Get database URL from Supabase settings."""
    settings = get_settings()
    # Extract database URL from Supabase URL
    # Format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
    return settings.supabase_url.replace("https://", "postgresql://postgres:").replace(".supabase.co", ".supabase.co:5432/postgres")

# Memory optimization settings for Railway
MEMORY_SETTINGS = {
    "max_workers": 1,
    "worker_class": "uvicorn.workers.UvicornWorker",
    "worker_connections": 100,
    "max_requests": 1000,
    "max_requests_jitter": 50,
    "preload_app": True,
    "timeout": 120,
    "keepalive": 2,
}

# Export commonly used settings
settings = get_settings()
setup_logging() 