from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


def find_project_root(start_path: Path) -> Path:
    """
    Find the project root by looking for .git directory or pyproject.toml.
    Walks up the directory tree until it finds a marker of the project root.
    """
    current_path = start_path.resolve()
    while current_path != current_path.parent:
        if (current_path / ".git").is_dir() or (current_path / "pyproject.toml").is_file():
            return current_path
        current_path = current_path.parent
    return start_path.resolve()


def get_env_files() -> list[Path]:
    """
    Get list of environment files, checking if they exist.
    Returns only existing files to avoid Pydantic warnings.
    """
    service_env = Path(__file__).parent / ".env"
    root_env = find_project_root(Path(__file__)) / ".env"
    
    env_files = []
    if service_env.exists():
        env_files.append(service_env)
    if root_env.exists():
        env_files.append(root_env)
    
    return env_files


class DashboardSettings(BaseSettings):
    """Settings for the Streamlit dashboard service."""
    
    model_config = SettingsConfigDict(
        env_file=get_env_files(),  # Dynamic env file discovery with validation
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