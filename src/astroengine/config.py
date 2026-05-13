from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.1-flash-lite"
    db_path: str = "./data/astroengine.db"
    default_language: str = "es"
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
