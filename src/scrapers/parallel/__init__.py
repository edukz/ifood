"""
Scrapers paralelos para extração simultânea
"""

from .real_parallel_restaurant_scraper import RealParallelRestaurantScraper
from .windows_parallel_scraper import WindowsParallelScraper

__all__ = [
    'RealParallelRestaurantScraper', 
    'WindowsParallelScraper'
]