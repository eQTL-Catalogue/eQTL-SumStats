import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Only try to load .env file in development environments
try:
    from dotenv import load_dotenv

    # Only load .env if it exists
    if os.path.exists(".env"):
        load_dotenv()
except ImportError:
    # If dotenv isn't installed, continue without it
    pass


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
        env_file=".env" if os.path.exists(".env") else None,
        env_prefix="",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Print configuration on startup
        print(
            f"""MongoDB URI: {
                'configured'
                if self.mongo_uri != 'mongodb://localhost:27017'
                else 'using default'
                }"""
        )
        print(f"Database Name: {self.db_name}")


# Create a global settings instance
settings = Settings()
