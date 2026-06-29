from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "local"
    APP_NAME: str = "Core Caja Huancayo"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bd_caja_huancayo_core"
    SECRET_KEY: str = "dev_secret_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_BUCKET: str = "documentos"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
