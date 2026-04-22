import os
import sys
import django
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_shop.settings')
django.setup()

from django.conf import settings as django_settings  # noqa: E402


MEDIA_ROOT = django_settings.MEDIA_ROOT


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    COURIER_ID = int(os.getenv("COURIER_ID", "0"))
    FLORIST_ID = int(os.getenv("FLORIST_ID", "0"))
    DEBUG = os.getenv("DEBUG", "False") == "True"

settings = Settings()