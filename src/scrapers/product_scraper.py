#!/usr/bin/env python3
"""
Product Scraper - Refactored modular version
Main orchestration file for product scraping functionality
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import Playwright

from src.scrapers.ifood_scraper import IfoodScraper
from src.models.product import Product
from src.utils.helpers import ensure_directories
from src.database.database_adapter import get_database_manager
from src.utils.error_handler import (
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)

# Import modular components
from src.scrapers.product.navigation_handler import ProductNavigationHandler
from src.scrapers.product.scroll_handler import ProductScrollHandler
from src.scrapers.product.element_finder import ProductElementFinder
from src.scrapers.product.data_extractor import ProductDataExtractor


class ProductScraper(IfoodScraper):
    """Scraper específico para extrair produtos/cardápio dos restaurantes - Versão Modular"""
    
    def __init__(self, city: str = None, headless: bool = True):
        super().__init__(city, headless)
        self.products: List[Product] = []
        self.db = get_database_manager()
        self.current_restaurant = None
        self.current_restaurant_id = None
        
        # Initialize modular components
        self.navigation_handler = ProductNavigationHandler(self.logger)
        self.scroll_handler = ProductScrollHandler(self.logger, self.human)
        self.element_finder = ProductElementFinder(self.logger)
        self.data_extractor = ProductDataExtractor(
            self.logger, 
            self.current_restaurant, 
            self.current_restaurant_id
        )
        
        # Statistics tracking
        self.stats = {
            'navigation_attempts': 0,
            'scroll_attempts': 0,
            'products_found': 0,
            'products_extracted': 0,
            'errors': 0
        }
    
    def navigate_to_restaurant(self, restaurant_url: str, restaurant_name: str):
        """Navega para a página do restaurante usando handler modular"""
        self.current_restaurant = restaurant_name
        self.stats['navigation_attempts'] += 1
        
        try:
            # Update data extractor with current restaurant info
            self.data_extractor.current_restaurant = restaurant_name
            self.data_extractor.current_restaurant_id = self.current_restaurant_id
            
            # Use navigation handler
            result = self.navigation_handler.navigate_to_restaurant(
                self, restaurant_url, restaurant_name
            )
            
            if not result['success']:
                raise NavigationError(result['error'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"ERRO ao navegar para restaurante {restaurant_name}: {str(e)}")
            raise NavigationError(f"Falha ao navegar para restaurante: {str(e)}")
    
    def _wait_for_products_to_load(self):
        """Aguarda o carregamento dos produtos usando handler modular"""
        return self.navigation_handler.wait_for_products_to_load(self.page)
    
    @with_retry(max_attempts=2, delay=3.0)
    def extract_products(self):
        """Extrai dados dos produtos do restaurante atual usando componentes modulares"""
        self.logger.info(f"Iniciando extração de produtos do restaurante: {self.current_restaurant}")
        extraction_stats = {'total': 0, 'success': 0, 'errors': 0}
        
        try:
            # Aguarda produtos carregarem
            if not self._wait_for_products_to_load():
                self.logger.warning("Nenhum produto encontrado ou restaurante fechado")
                return extraction_stats
            
            # Faz scroll para carregar todos os produtos
            scroll_stats = self.scroll_handler.scroll_to_load_all_products(self.page)
            self.stats['scroll_attempts'] = scroll_stats.get('scroll_attempts', 0)
            
            # Busca produtos usando elemento finder
            product_elements = self.element_finder.find_product_elements(self.page)
            extraction_stats['total'] = len(product_elements)
            self.stats['products_found'] = len(product_elements)
            
            if len(product_elements) == 0:
                self.logger.warning("Nenhum produto encontrado após busca")
                return extraction_stats
            
            self.logger.info(f"Encontrados {len(product_elements)} produtos para extrair")
            
            # Extrai dados de cada produto usando data extractor
            for i, element in enumerate(product_elements, 1):
                try:
                    product_data = self.data_extractor.extract_product_data(
                        element, i, extraction_stats['total']
                    )
                    
                    if product_data and self.data_extractor.validate_extracted_data(product_data):
                        product = Product(**product_data)
                        self.products.append(product)
                        extraction_stats['success'] += 1
                        self.stats['products_extracted'] += 1
                        self.logger.info(f"SUCESSO [{i}/{extraction_stats['total']}] {product_data['nome'][:50]}...")
                    else:
                        extraction_stats['errors'] += 1
                        self.logger.debug(f"Produto {i} não passou na validação")
                    
                    # Pequeno delay entre extrações
                    self.human.random_delay(0.1, 0.3)
                    
                except Exception as e:
                    extraction_stats['errors'] += 1
                    self.stats['errors'] += 1
                    self.logger.warning(f"ERRO [{i}/{extraction_stats['total']}] Erro ao extrair produto: {str(e)[:100]}")
                    continue
            
            # Resumo da extração
            self.logger.info(f"\nResumo da extração de produtos:")
            self.logger.info(f"  Total encontrado: {extraction_stats['total']}")
            self.logger.info(f"  Sucesso: {extraction_stats['success']}")
            self.logger.info(f"  Erros: {extraction_stats['errors']}")
            
            return extraction_stats
            
        except Exception as e:
            self.logger.error(f"ERRO durante extração de produtos: {str(e)}")
            raise DataExtractionError(f"Erro ao extrair produtos: {str(e)}")
    
    def save_products(self):
        """Salva os produtos no banco de dados"""
        ensure_directories()
        
        if not self.products:
            self.logger.warning("Nenhum produto para salvar")
            return {'new': 0, 'duplicates': 0, 'total': 0}
        
        # Converte produtos para formato dict
        products_data = [prod.to_dict() for prod in self.products]
        
        # Analisa estatísticas dos produtos antes de salvar
        price_stats = self.data_extractor.get_price_statistics(products_data)
        self.logger.info(f"Estatísticas de preços: {price_stats}")
        
        # Salva no banco de dados
        result = self.db.save_products(
            products_data, 
            self.current_restaurant, 
            self.current_restaurant_id
        )
        
        self.logger.info(f"Resumo do salvamento de produtos:")
        self.logger.info(f"  Novos produtos: {result['new']}")
        self.logger.info(f"  Duplicados (ignorados): {result['duplicates']}")
        self.logger.info(f"  Total no arquivo: {result['total']}")
        self.logger.info(f"  Arquivo: {result.get('file', 'N/A')}")
        
        return result
    
    def run_for_restaurant(self, playwright: Playwright, restaurant_url: str, 
                          restaurant_name: str, restaurant_id: str):
        """Executa o scraping para um restaurante específico"""
        ensure_directories()
        self.current_restaurant_id = restaurant_id
        
        # Reset statistics
        self.stats = {
            'navigation_attempts': 0,
            'scroll_attempts': 0,
            'products_found': 0,
            'products_extracted': 0,
            'errors': 0
        }
        
        try:
            self.setup_browser(playwright)
            self.navigate_to_restaurant(restaurant_url, restaurant_name)
            extraction_stats = self.extract_products()
            save_result = self.save_products()
            
            # Compile final statistics
            final_stats = {
                'success': True,
                'restaurant': restaurant_name,
                'products_found': len(self.products),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'products': self.products,
                'extraction_stats': extraction_stats,
                'scraper_stats': self.stats
            }
            
            self.logger.info(f"Scraping concluído para {restaurant_name}: {final_stats}")
            return final_stats
            
        except Exception as e:
            self.logger.error(f"ERRO durante execução para {restaurant_name}: {e}")
            return {
                'success': False,
                'restaurant': restaurant_name,
                'error': str(e),
                'products_found': 0,
                'scraper_stats': self.stats
            }
            
        finally:
            self.cleanup()
    
    def get_scraper_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o scraper modular"""
        return {
            'version': '2.0.0',
            'type': 'modular',
            'components': {
                'navigation_handler': self.navigation_handler.__class__.__name__,
                'scroll_handler': self.scroll_handler.__class__.__name__,
                'element_finder': self.element_finder.__class__.__name__,
                'data_extractor': self.data_extractor.__class__.__name__
            },
            'statistics': self.stats,
            'modular_stats': {
                'navigation': self.navigation_handler.get_navigation_statistics(),
                'scroll': self.scroll_handler.get_scroll_statistics(),
                'element_finder': self.element_finder.get_finder_statistics(),
                'data_extractor': self.data_extractor.get_extraction_statistics()
            }
        }
    
    def verify_restaurant_page(self, restaurant_name: str) -> Dict[str, Any]:
        """Verifica se a página do restaurante está válida"""
        return self.navigation_handler.verify_restaurant_page(self.page, restaurant_name)
    
    def count_products_on_page(self) -> int:
        """Conta produtos na página atual"""
        return self.element_finder.count_products_on_page(self.page)
    
    def get_element_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos elementos encontrados"""
        if hasattr(self, '_last_elements'):
            return self.element_finder.get_element_statistics(self._last_elements)
        return {}
    
    def force_scroll_and_count(self) -> Dict[str, Any]:
        """Força scroll e retorna estatísticas detalhadas"""
        scroll_stats = self.scroll_handler.scroll_to_load_all_products(self.page)
        final_count = self.element_finder.count_products_on_page(self.page)
        
        return {
            'scroll_stats': scroll_stats,
            'final_product_count': final_count,
            'performance': {
                'products_per_scroll': final_count / max(scroll_stats.get('scroll_attempts', 1), 1),
                'efficiency': scroll_stats.get('products_loaded', 0) / max(scroll_stats.get('scroll_attempts', 1), 1)
            }
        }


# Backward compatibility - Legacy methods for existing integrations
class ProductScraperLegacy(ProductScraper):
    """Classe de compatibilidade com versão anterior"""
    
    def _scroll_to_load_all_products(self):
        """Método legacy - usa novo handler"""
        return self.scroll_handler.scroll_to_load_all_products(self.page)
    
    def _find_product_elements(self):
        """Método legacy - usa novo finder"""
        return self.element_finder.find_product_elements(self.page)
    
    def _extract_product_data(self, element, index: int, total: int):
        """Método legacy - usa novo extractor"""
        return self.data_extractor.extract_product_data(element, index, total)
    
    def _count_visible_products(self):
        """Método legacy - usa novo counter"""
        return self.element_finder.count_products_on_page(self.page)