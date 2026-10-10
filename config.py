from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./habits.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Baku")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

settings = Settings()
