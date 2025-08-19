from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class DashboardSettings(BaseSettings):
    """Settings for the Streamlit dashboard service."""
    
    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent / ".env",  # Service-specific .env
            Path(__file__).parent.parent / ".env",  # Root .env
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Dashboard-specific settings
    dashboard_host: str = "localhost"
    dashboard_port: int = 8501
    theme: str = "light"
    title: str = "TwinRAD Dashboard"
    
    # Inherited settings
    log_level: str = "INFO"
    
    # Optional: API keys that might be needed for dashboard
    gooelg_genai_api_key: str = ""
    twinkle_base_url: str = ""
    twinkle_api_key: str = ""