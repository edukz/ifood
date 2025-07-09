#!/usr/bin/env python3
"""
Módulo Windows Parallel Scraper - Pacote modular para scraping paralelo otimizado para Windows
"""

from .windows_parallel_scraper import WindowsParallelScraper, detect_windows
from .windows_data_generator import WindowsDataGenerator
from .windows_data_processor import WindowsDataProcessor
from .windows_database_manager import WindowsDatabaseManager

__all__ = ['WindowsParallelScraper', 'detect_windows', 'WindowsDataGenerator', 'WindowsDataProcessor', 'WindowsDatabaseManager']