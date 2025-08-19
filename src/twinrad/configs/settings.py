from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class TwinRADSettings(BaseSettings):
    """
    Core TwinRAD settings for the multi-agent red teaming framework.
    This class handles configuration for the core twinrad package only.
    Service-specific settings (server, dashboard) are handled separately.
    """
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent.parent.parent.parent / ".env",  # Root .env
        ],
        env_file_encoding='utf-8',
        extra="ignore"
    )

    # Core TwinRAD settings
    log_level: str = "INFO"
    
    # LLM API Keys for red team agents
    gooelg_genai_api_key: str = ''
    twinkle_base_url: HttpUrl = HttpUrl('http://localhost')
    twinkle_api_key: str = ''
    
    # Red team specific settings
    max_rounds: int = 20
    conversation_timeout: int = 300  # seconds
    safety_threshold: float = 0.8

# Create an instance of the Settings class
settings = TwinRADSettings()