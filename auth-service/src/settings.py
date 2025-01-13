from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URI: str