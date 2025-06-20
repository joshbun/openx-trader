from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    MOBEE_OPEN_API_URL = os.getenv("MOBEE_OPEN_API_URL")
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")


settings = Settings()
