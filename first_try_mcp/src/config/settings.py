"""
Application settings and configuration management.

This module loads configuration from YAML file with validation and type safety.
"""

from typing import Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
import yaml


class ServerConfig(BaseModel):
    """Server configuration."""
    name: str = Field(default="Enterprise MCP Server")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1024, le=65535)
    transport: Literal["http", "stdio"] = Field(default="http")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    format: Literal["json", "text"] = Field(default="json")
    file: str | None = Field(default="logs/mcp_server.log")


class APIConfig(BaseModel):
    """API configuration."""
    request_timeout: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=1.0, ge=0.1)


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    enable_weather_tool: bool = Field(default=True)
    enable_ip_info_tool: bool = Field(default=True)
    enable_dictionary_tool: bool = Field(default=True)
    enable_exchange_rate_tool: bool = Field(default=True)


class DevelopmentConfig(BaseModel):
    """Development settings configuration."""
    debug_mode: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(default="development")


class Settings(BaseModel):
    """Application settings loaded from YAML configuration."""
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    
    @classmethod
    def load_from_yaml(cls, config_path: str | Path = "config.yaml") -> "Settings":
        """
        Load settings from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Settings instance
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"Warning: Config file {config_path} not found, using defaults")
            return cls()
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                print(f"Warning: Config file {config_path} is empty, using defaults")
                return cls()
                
            return cls(**config_data)
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}")
            print("Using default configuration")
            return cls()
    
    # Convenience properties for backward compatibility
    @property
    def server_name(self) -> str:
        return self.server.name
    
    @property
    def server_host(self) -> str:
        return self.server.host
    
    @property
    def server_port(self) -> int:
        return self.server.port
    
    @property
    def transport(self) -> str:
        return self.server.transport
    
    @property
    def log_level(self) -> str:
        return self.logging.level
    
    @property
    def log_format(self) -> str:
        return self.logging.format
    
    @property
    def log_file(self) -> str | None:
        return self.logging.file
    
    @property
    def request_timeout(self) -> int:
        return self.api.request_timeout
    
    @property
    def max_retries(self) -> int:
        return self.api.max_retries
    
    @property
    def retry_delay(self) -> float:
        return self.api.retry_delay
    
    @property
    def enable_weather_tool(self) -> bool:
        return self.features.enable_weather_tool
    
    @property
    def enable_ip_info_tool(self) -> bool:
        return self.features.enable_ip_info_tool
    
    @property
    def enable_dictionary_tool(self) -> bool:
        return self.features.enable_dictionary_tool
    
    @property
    def enable_exchange_rate_tool(self) -> bool:
        return self.features.enable_exchange_rate_tool
    
    @property
    def debug_mode(self) -> bool:
        return self.development.debug_mode
    
    @property
    def environment(self) -> str:
        return self.development.environment


# Global settings instance - load from YAML
settings = Settings.load_from_yaml()
