"""
Configuration loader for CryptoGuardLite
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration management class"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = os.path.join(
                Path(__file__).parent.parent.parent,
                "config",
                "config.yaml"
            )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return self.config.get('data', {})
    
    @property
    def model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return self.config.get('model', {})
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.config.get('api', {})
    
    @property
    def training_config(self) -> Dict[str, Any]:
        """Get training configuration"""
        return self.config.get('training', {})


# Global configuration instance
config = Config()
