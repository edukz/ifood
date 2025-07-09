"""
Configuration Module - Modular configuration system for the iFood scraper
"""

from .config_base import ConfigBase
from .database_config import DatabaseConfig
from .network_config import NetworkConfig
from .file_config import FileConfig
from .scraping_config import ScrapingConfig
from .system_config import SystemConfig
from .backup_config import BackupConfig

__all__ = [
    'ConfigBase',
    'DatabaseConfig',
    'NetworkConfig',
    'FileConfig',
    'ScrapingConfig',
    'SystemConfig',
    'BackupConfig'
]