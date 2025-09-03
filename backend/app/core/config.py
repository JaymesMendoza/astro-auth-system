from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # JWT
    jwt_secret: str = "your-super-secret-jwt-key-change-in-production-min-32-chars"
    jwt_refresh_secret: str = "your-super-secret-refresh-key-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@yourdomain.com"
    
    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Application
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:4321"
    environment: str = "development"
    
    # Security
    bcrypt_rounds: int = 12
    rate_limit_per_minute: int = 100
    login_rate_limit_per_15min: int = 5
    password_reset_rate_limit_per_hour: int = 3
    
    # CORS
    cors_origins: List[str] = ["http://localhost:4321", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()