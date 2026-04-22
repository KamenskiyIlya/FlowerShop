import os
import sys
from pathlib import Path

import django
from django.apps import apps


def ensure_django() -> None:
    if apps.ready:
        return

    project_root = Path(__file__).resolve().parents[2]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_shop.settings")
    django.setup()
