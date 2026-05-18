from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
import os


class Settings(BaseSettings):
    APP_NAME: str = "CoreInventory"
    APP_ENV: str = "development"
    SECRET_KEY: str
    FRONTEND_URL: AnyHttpUrl = "http://localhost:5173"

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "coreinventory"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        # If running inside Docker and DATABASE_URL points to localhost,
        # replace it with 'db' (the service name in docker-compose)
        is_docker = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"
        if is_docker:
            if "localhost" in v or "127.0.0.1" in v:
                v = v.replace("localhost", "db").replace("127.0.0.1", "db")
        else:
            # On local Windows, sometimes 'localhost' resolves to IPv6 or fails in some drivers
            # Force 127.0.0.1 for stability
            if "localhost" in v:
                v = v.replace("localhost", "127.0.0.1")
        
        # Debug print to verify the URL being used
        if os.environ.get("DOCKER_CONTAINER") == "true":
            print(f"[DEBUG] Using Database URL: {v}")
            
        return v

    # JWT
    JWT_SECRET: str
    JWT_LIFETIME_SECONDS: int = 3600
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 86400

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = "CoreInventory"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
