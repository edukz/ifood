"""
Product Scraper Module - Estrutura modular para scraping de produtos
"""

from .selectors import ProductSelectors
from .navigation_handler import ProductNavigationHandler
from .scroll_handler import ProductScrollHandler
from .element_finder import ProductElementFinder
from .data_extractor import ProductDataExtractor

__all__ = [
    'ProductSelectors',
    'ProductNavigationHandler',
    'ProductScrollHandler',
    'ProductElementFinder',
    'ProductDataExtractor'
]