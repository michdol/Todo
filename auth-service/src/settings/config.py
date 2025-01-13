import os

from src.settings.base import Settings
from src.settings.test import TestSettings


def get_settings():
    if os.getenv("STAGE") == "test":
        return TestSettings()
    else:
        return Settings()


settings = get_settings()