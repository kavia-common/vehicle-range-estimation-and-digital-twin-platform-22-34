import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment with defaults."""
    APP_NAME: str = "Vehicle Range Backend"
    VERSION: str = "0.1.0"
    PORT: int = 3001
    DATA_DIR: str = "./data"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_prefix = ""
        case_sensitive = False


_settings: Optional[Settings] = None


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Get singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# PUBLIC_INTERFACE
def ensure_data_dirs() -> None:
    """Ensure data directories exist under DATA_DIR."""
    s = get_settings()
    base = os.path.abspath(s.DATA_DIR)
    twins = os.path.join(base, "twins")
    exports = os.path.join(base, "exports")

    for path in (base, twins, exports):
        os.makedirs(path, exist_ok=True)
