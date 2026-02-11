"""
Utility functions for CryptoGuardLite
"""
from .config import Config, config
from .logger import setup_logger, default_logger

__all__ = ['Config', 'config', 'setup_logger', 'default_logger']
