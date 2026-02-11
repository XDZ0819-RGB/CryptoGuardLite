"""
Test configuration and utilities
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import Config


def test_config_loading():
    """Test configuration loading"""
    cfg = Config()
    assert cfg.config is not None
    assert isinstance(cfg.config, dict)


def test_config_get():
    """Test configuration get method"""
    cfg = Config()
    
    # Test existing key
    data_config = cfg.get('data')
    assert data_config is not None
    
    # Test nested key
    raw_dir = cfg.get('data.raw_data_dir')
    assert raw_dir == "data/raw"
    
    # Test non-existing key with default
    non_existing = cfg.get('non.existing.key', 'default')
    assert non_existing == 'default'


def test_config_properties():
    """Test configuration properties"""
    cfg = Config()
    
    assert cfg.data_config is not None
    assert cfg.model_config is not None
    assert cfg.api_config is not None
    assert cfg.training_config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
