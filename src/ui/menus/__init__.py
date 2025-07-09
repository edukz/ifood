"""
Menus especializados para o sistema iFood Scraper
"""

from .search_menus import SearchMenus
from .parallel_menus import ParallelMenus
from .reports_menus import ReportsMenus
from .config_menus import ConfigMenus
from .status_menus import StatusMenus
from .archive_menus import ArchiveMenus

__all__ = [
    'SearchMenus',
    'ParallelMenus', 
    'ReportsMenus',
    'ConfigMenus',
    'StatusMenus',
    'ArchiveMenus'
]