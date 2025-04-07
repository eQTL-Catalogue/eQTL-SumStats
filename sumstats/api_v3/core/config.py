# For Pydantic v2
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings.

    These settings can be configured through environment variables.
    """

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # MongoDB connection settings
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "eqtl_db"

    # API configuration
    api_title: str = "eQTL API with MongoDB"
    api_prefix: str = "/api/v3"

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    # Logging configuration
    log_level: str = "INFO"

    # In Pydantic v2, model_config replaces the inner Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )


# Create a global settings instance
settings = Settings()
