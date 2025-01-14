from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    STAGE: str = "base"
    DATABASE_URI: str
    SECRET_KEY: str
