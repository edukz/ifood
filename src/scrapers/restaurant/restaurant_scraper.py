#!/usr/bin/env python3
"""
Restaurant Scraper - Main orchestration class for restaurant scraping
Refactored into modular components for better maintainability
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from playwright.sync_api import Playwright, TimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Fallback classes
    class Playwright:
        pass
    class TimeoutError(Exception):
        pass

from src.scrapers.ifood_scraper import IfoodScraper
from src.models.restaurant import Restaurant
from src.utils.helpers import ensure_directories
from src.database.database_adapter import get_database_manager
from src.utils.error_handler import (
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)
from src.config.settings import SETTINGS

# Import modular components
from .selectors import RestaurantSelectors
from .element_finder import RestaurantElementFinder
from .scroll_handler import ScrollHandler
from .data_extractor import RestaurantDataExtractor
from .navigation_handler import NavigationHandler


class RestaurantScraper(IfoodScraper):
    """
    Scraper específico para extrair dados dos restaurantes
    Refatorado com arquitetura modular para melhor manutenibilidade
    """
    
    def __init__(self, city: str = None, headless: bool = False):
        super().__init__(city, headless)
        self.restaurants: List[Restaurant] = []
        self.restaurants_container_xpath = '//*[@id="__next"]/div[1]/main/div/section/article'
        self.db = get_database_manager()
        self.current_category = None
        
        # Initialize modular components
        self.selectors = RestaurantSelectors()
        self.element_finder = RestaurantElementFinder(self.logger)
        self.scroll_handler = ScrollHandler(self.logger, self.human)
        self.data_extractor = RestaurantDataExtractor(self.logger)
        self.navigation_handler = NavigationHandler(self.logger)
        
        self.logger.info("RestaurantScraper inicializado com arquitetura modular")
    
    def navigate_to_category(self, category_url: str, category_name: str):
        """
        Navega para uma categoria específica usando o NavigationHandler
        
        Args:
            category_url: URL of the category to navigate to
            category_name: Name of the category
        """
        self.current_category = category_name
        
        # Update data extractor with current category
        self.data_extractor.current_category = category_name
        
        # Use navigation handler
        result = self.navigation_handler.navigate_to_category(
            self, category_url, category_name
        )
        
        if not result['success']:
            raise NavigationError(result['error'])
        
        # Verify that the category page loaded correctly
        verification = self.navigation_handler.verify_category_page(
            self.page, category_name
        )
        
        if not verification['is_valid']:
            error_msg = f"Página da categoria {category_name} não carregou corretamente"
            if verification['warnings']:
                error_msg += f". Warnings: {', '.join(verification['warnings'])}"
            raise NavigationError(error_msg)
    
    @with_retry(max_attempts=2, delay=3.0)
    def extract_restaurants(self):
        """
        Extrai dados dos restaurantes da categoria atual usando componentes modulares
        """
        self.logger.info(f"Iniciando extração de restaurantes da categoria: {self.current_category}")
        extraction_stats = {'total': 0, 'success': 0, 'errors': 0}
        
        try:
            # Aguarda container de restaurantes
            self.logger.info("Aguardando container de restaurantes...")
            try:
                self.page.wait_for_selector(self.restaurants_container_xpath, timeout=15000, state="visible")
            except TimeoutError:
                self.error_handler.take_screenshot(self.page, "restaurants_container_timeout")
                self.error_handler.log_page_state(self.page)
                raise DataExtractionError("Container de restaurantes não encontrado")
            
            self.human.random_wait()
            
            # Scroll para carregar mais restaurantes usando ScrollHandler
            self.logger.info("Fazendo scroll para carregar restaurantes...")
            scroll_stats = self.scroll_handler.scroll_to_load_restaurants(
                self.page, 
                lambda: self.element_finder.count_restaurants_on_page(self.page)
            )
            
            self.logger.info(f"Scroll concluído: {scroll_stats}")
            
            # Busca todos os elementos de restaurantes usando ElementFinder
            restaurant_elements = self.element_finder.find_restaurant_elements(self.page)
            extraction_stats['total'] = len(restaurant_elements)
            
            if len(restaurant_elements) == 0:
                self.error_handler.take_screenshot(self.page, "no_restaurants_found")
                raise DataExtractionError("Nenhum restaurante encontrado")
            
            # Extrai dados de cada restaurante usando DataExtractor
            for i, element in enumerate(restaurant_elements, 1):
                try:
                    restaurant_data = self.data_extractor.extract_restaurant_data(
                        element, i, extraction_stats['total']
                    )
                    
                    if restaurant_data and self.data_extractor.validate_extracted_data(restaurant_data):
                        restaurant = Restaurant(**restaurant_data)
                        self.restaurants.append(restaurant)
                        extraction_stats['success'] += 1
                        self.logger.info(f"SUCESSO [{i}/{extraction_stats['total']}] {restaurant_data['nome']}")
                    else:
                        self.logger.debug(f"AVISO [{i}/{extraction_stats['total']}] Restaurante ignorado (dados inválidos)")
                    
                    # Delay entre extrações
                    self.human.random_delay(0.2, 0.5)
                    
                except Exception as e:
                    extraction_stats['errors'] += 1
                    self.logger.warning(f"ERRO [{i}/{extraction_stats['total']}] Erro ao extrair restaurante: {str(e)[:100]}")
                    continue
            
            # Resumo da extração
            self._log_extraction_summary(extraction_stats, scroll_stats)
            
            if len(self.restaurants) == 0:
                self.error_handler.take_screenshot(self.page, "no_restaurants_extracted")
                raise DataExtractionError("Nenhum restaurante foi extraído com sucesso")
            
        except (TimeoutError, DataExtractionError) as e:
            self.logger.error(f"ERRO durante extração: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"ERRO inesperado: {str(e)}")
            self.error_handler.take_screenshot(self.page, "unexpected_extraction_error")
            raise DataExtractionError(f"Erro ao extrair restaurantes: {str(e)}")
    
    def _log_extraction_summary(self, extraction_stats: Dict[str, int], scroll_stats: Dict[str, Any]):
        """Log detailed extraction summary"""
        self.logger.info(f"\n=== RESUMO DA EXTRAÇÃO ===")
        self.logger.info(f"Categoria: {self.current_category}")
        self.logger.info(f"Total encontrado: {extraction_stats['total']}")
        self.logger.info(f"Sucesso: {extraction_stats['success']}")
        self.logger.info(f"Erros: {extraction_stats['errors']}")
        self.logger.info(f"Taxa de sucesso: {extraction_stats['success']/extraction_stats['total']*100:.1f}%")
        self.logger.info(f"Scroll - Inicial: {scroll_stats.get('initial_count', 0)}, Final: {scroll_stats.get('final_count', 0)}")
        self.logger.info(f"Scroll - Tentativas: {scroll_stats.get('scroll_attempts', 0)}, Botões: {scroll_stats.get('buttons_clicked', 0)}")
        self.logger.info(f"=========================")
    
    def save_restaurants(self):
        """
        Salva os restaurantes no banco de dados
        """
        ensure_directories()
        
        if not self.restaurants:
            self.logger.warning("AVISO: Nenhum restaurante para salvar")
            return {'new': 0, 'duplicates': 0, 'total': 0}
        
        # Converte restaurantes para formato dict
        restaurants_data = [rest.to_dict() for rest in self.restaurants]
        
        # Salva no banco de dados
        result = self.db.save_restaurants(
            restaurants_data, 
            self.current_category or "indefinido", 
            self.city
        )
        
        # Log detalhado do salvamento
        self._log_save_summary(result)
        
        return result
    
    def _log_save_summary(self, result: Dict[str, Any]):
        """Log detailed save summary"""
        self.logger.info(f"\n=== RESUMO DO SALVAMENTO ===")
        self.logger.info(f"Categoria: {self.current_category}")
        self.logger.info(f"Cidade: {self.city}")
        self.logger.info(f"Novos restaurantes: {result['new']}")
        self.logger.info(f"Duplicados (atualizados): {result['duplicates']}")
        self.logger.info(f"Total processado: {result['total']}")
        self.logger.info(f"Status: {result.get('status', 'Concluído')}")
        self.logger.info(f"============================")
    
    def run_for_category(self, playwright: Playwright, category_url: str, category_name: str):
        """
        Executa o scraping para uma categoria específica
        
        Args:
            playwright: Playwright instance
            category_url: URL of the category to scrape
            category_name: Name of the category
            
        Returns:
            Dictionary with execution results
        """
        ensure_directories()
        
        execution_start = datetime.now()
        
        try:
            # Setup browser
            self.setup_browser(playwright)
            
            # Navigate to category
            self.navigate_to_category(category_url, category_name)
            
            # Extract restaurants
            self.extract_restaurants()
            
            # Save results
            save_result = self.save_restaurants()
            
            # Calculate execution time
            execution_time = datetime.now() - execution_start
            
            # Return detailed results
            return {
                'success': True,
                'category': category_name,
                'url': category_url,
                'execution_time': str(execution_time),
                'restaurants_found': len(self.restaurants),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'total_in_db': save_result['total'],
                'restaurants': self.restaurants,
                'components_used': {
                    'selectors': type(self.selectors).__name__,
                    'element_finder': type(self.element_finder).__name__,
                    'scroll_handler': type(self.scroll_handler).__name__,
                    'data_extractor': type(self.data_extractor).__name__,
                    'navigation_handler': type(self.navigation_handler).__name__
                }
            }
            
        except Exception as e:
            execution_time = datetime.now() - execution_start
            self.logger.error(f"ERRO durante execução para {category_name}: {e}")
            
            return {
                'success': False,
                'category': category_name,
                'url': category_url,
                'execution_time': str(execution_time),
                'error': str(e),
                'restaurants_found': len(self.restaurants),
                'components_used': {
                    'selectors': type(self.selectors).__name__,
                    'element_finder': type(self.element_finder).__name__,
                    'scroll_handler': type(self.scroll_handler).__name__,
                    'data_extractor': type(self.data_extractor).__name__,
                    'navigation_handler': type(self.navigation_handler).__name__
                }
            }
            
        finally:
            # Remove pausa automática - apenas fecha o navegador
            self.cleanup()
    
    def get_scraper_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do scraper"""
        return {
            'architecture': 'Modular',
            'components': {
                'selectors': self.selectors.get_scraper_statistics() if hasattr(self.selectors, 'get_scraper_statistics') else 'Loaded',
                'element_finder': 'Loaded',
                'scroll_handler': self.scroll_handler.get_scroll_statistics(),
                'data_extractor': self.data_extractor.get_extraction_statistics(),
                'navigation_handler': self.navigation_handler.get_navigation_statistics()
            },
            'current_session': {
                'category': self.current_category,
                'city': self.city,
                'restaurants_extracted': len(self.restaurants)
            }
        }