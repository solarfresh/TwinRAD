from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class ServerSettings(BaseSettings):
    """Settings for the Socket.IO server service."""
    
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent / ".env",  # Service-specific .env
            Path(__file__).parent.parent / ".env",  # Root .env
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Server-specific settings
    server_host: str = "localhost"
    server_port: int = 5000
    debug: bool = False
    
    # Inherited from root .env if not overridden
    log_level: str = "INFO"
    
    # Optional: API keys that might be needed for server
    gooelg_genai_api_key: str = ""
    twinkle_base_url: str = ""
    twinkle_api_key: str = ""