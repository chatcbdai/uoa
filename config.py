# config.py - Configuration management with environment variables
import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class LLMConfig(BaseSettings):
    """LLM configuration settings"""
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field(default="gpt-4o", env="DEFAULT_MODEL")  # Using GPT-4o for efficiency
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment

class BrowserConfig(BaseSettings):
    """Browser configuration settings"""
    default_engine: str = Field(default="stealth", env="DEFAULT_BROWSER_ENGINE")
    headless: bool = Field(default=True, env="HEADLESS_MODE")
    anti_detection: bool = Field(default=True, env="ANTI_DETECTION")
    viewport_width: int = Field(default=1920, env="VIEWPORT_WIDTH")
    viewport_height: int = Field(default=1080, env="VIEWPORT_HEIGHT")
    user_agent: Optional[str] = Field(default=None, env="CUSTOM_USER_AGENT")
    proxy: Optional[str] = Field(default=None, env="PROXY_URL")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment

class ExecutionConfig(BaseSettings):
    """Task execution configuration"""
    max_concurrent_tasks: int = Field(default=3, env="MAX_CONCURRENT_TASKS")
    task_timeout: int = Field(default=300, env="TASK_TIMEOUT")  # seconds
    rate_limit: float = Field(default=1.0, env="RATE_LIMIT")  # requests per second
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment

class StorageConfig(BaseSettings):
    """Storage configuration"""
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    screenshots_dir: Path = Field(default=Path("./screenshots"), env="SCREENSHOTS_DIR")
    results_dir: Path = Field(default=Path("./results"), env="RESULTS_DIR")
    cache_dir: Path = Field(default=Path("./cache"), env="CACHE_DIR")
    db_path: Path = Field(default=Path("./data/assistant.db"), env="DB_PATH")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        for dir_path in [self.data_dir, self.screenshots_dir, self.results_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment

class SocialMediaConfig(BaseSettings):
    """Social media configuration"""
    enabled: bool = Field(default=True, env="SOCIAL_MEDIA_ENABLED")
    headless: bool = Field(default=False, env="SOCIAL_MEDIA_HEADLESS")
    post_delay_min: int = Field(default=5, env="POST_DELAY_MIN")
    post_delay_max: int = Field(default=10, env="POST_DELAY_MAX")
    max_retries: int = Field(default=3, env="SOCIAL_MEDIA_MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class Config:
    """Main configuration class"""
    def __init__(self):
        self.llm = LLMConfig()
        self.browser = BrowserConfig()
        self.execution = ExecutionConfig()
        self.storage = StorageConfig()
        self.social_media = SocialMediaConfig()
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check LLM API keys
        if self.llm.default_provider == "openai" and not self.llm.openai_api_key:
            errors.append("OpenAI API key not set")
        elif self.llm.default_provider == "anthropic" and not self.llm.anthropic_api_key:
            errors.append("Anthropic API key not set")
        
        # Check browser engine
        valid_engines = ["stealth", "playwright", "camoufox", "static"]
        if self.browser.default_engine not in valid_engines:
            errors.append(f"Invalid browser engine: {self.browser.default_engine}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "llm": self.llm.dict(),
            "browser": self.browser.dict(),
            "execution": self.execution.dict(),
            "storage": self.storage.dict(),
            "social_media": self.social_media.dict()
        }

# Global configuration instance
config = Config()