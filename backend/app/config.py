"""
Application Configuration and Environment Settings.
"""

import os
from typing import List, Literal, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings parsed from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Basics
    PROJECT_NAME: str = "Video2Content"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "insecure_dev_secret_key_minimum_32_characters_long_12345"

    # API & CORS
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            import json
            return json.loads(v)
        elif isinstance(v, list):
            return v
        return ["*"]

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "videoscribe"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/videoscribe"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Object Storage (S3 / MinIO)
    STORAGE_TYPE: Literal["s3", "minio", "local"] = "minio"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "video2content-media"
    S3_REGION: str = "us-east-1"

    # Speech-to-Text Provider
    STT_PROVIDER: Literal["mock", "openai", "faster_whisper"] = "mock"
    OPENAI_API_KEY: str = ""

    # Processing & Media Limits
    TEMP_MEDIA_DIR: str = "./tmp/media"
    MAX_UPLOAD_SIZE_MB: int = 500
    MAX_VIDEO_DURATION_SECONDS: int = 7200  # 2 hours max for V1

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
