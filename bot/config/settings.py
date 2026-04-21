import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    COURIER_ID = int(os.getenv("COURIER_ID", "0"))
    FLORIST_ID = int(os.getenv("FLORIST_ID", "0"))
    DEBUG = os.getenv("DEBUG", "False") == "True"

settings = Settings()