"""
Restaurant Scraper Module - Estrutura modular para scraping de restaurantes
"""

from .restaurant_scraper import RestaurantScraper
from .selectors import RestaurantSelectors
from .element_finder import RestaurantElementFinder
from .scroll_handler import ScrollHandler
from .data_extractor import RestaurantDataExtractor
from .navigation_handler import NavigationHandler

__all__ = [
    'RestaurantScraper',
    'RestaurantSelectors',
    'RestaurantElementFinder',
    'ScrollHandler', 
    'RestaurantDataExtractor',
    'NavigationHandler'
]