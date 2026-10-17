from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    PROJECT_NAME = "AI Resume Platform"

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-development")

    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
    MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    VECTOR_DATA_DIR = os.getenv("VECTOR_DATA_DIR", "vector_data")
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "disabled").lower()
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    RECRUITER_CONTACT_EMAIL = os.getenv("RECRUITER_CONTACT_EMAIL")
    MAX_INVITATION_BATCH_SIZE = int(os.getenv("MAX_INVITATION_BATCH_SIZE", "50"))

settings = Settings()
