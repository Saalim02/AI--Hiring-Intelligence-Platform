from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    PROJECT_NAME = "AI Resume Platform"

    SECRET_KEY = os.getenv("SECRET_KEY")

    ALGORITHM = os.getenv("ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()