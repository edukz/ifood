#!/usr/bin/env python3
"""
Restaurant Scraper V2 - Interface de compatibilidade para o RestaurantScraper modular
Mantém a mesma interface da versão anterior para compatibilidade
"""

# Import the modular version
from .restaurant.restaurant_scraper import RestaurantScraper as ModularRestaurantScraper
from .restaurant import (
    RestaurantSelectors,
    RestaurantElementFinder,
    ScrollHandler,
    RestaurantDataExtractor,
    NavigationHandler
)

# Export the modular version with the same interface
class RestaurantScraper(ModularRestaurantScraper):
    """
    Interface de compatibilidade para o RestaurantScraper modular
    Mantém a mesma interface da versão anterior
    """
    
    def __init__(self, city: str = None, headless: bool = False):
        super().__init__(city, headless)
        self.logger.info("RestaurantScraper V2 (Modular) inicializado")
    
    def get_version_info(self):
        """Retorna informações da versão"""
        return {
            'version': '2.0.0',
            'architecture': 'Modular',
            'components': [
                'RestaurantSelectors',
                'RestaurantElementFinder', 
                'ScrollHandler',
                'RestaurantDataExtractor',
                'NavigationHandler'
            ],
            'compatibility': 'Fully compatible with v1.0 interface',
            'performance': 'Improved maintainability and testability',
            'file_structure': {
                'main': 'src/scrapers/restaurant/restaurant_scraper.py',
                'modules': [
                    'src/scrapers/restaurant/selectors.py',
                    'src/scrapers/restaurant/element_finder.py',
                    'src/scrapers/restaurant/scroll_handler.py',
                    'src/scrapers/restaurant/data_extractor.py',
                    'src/scrapers/restaurant/navigation_handler.py'
                ]
            }
        }

# Maintain backward compatibility
__all__ = ['RestaurantScraper']