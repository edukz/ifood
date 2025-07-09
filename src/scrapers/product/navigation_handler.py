#!/usr/bin/env python3
"""
Product Navigation Handler - Navigation and page management for product scraping
"""

from typing import Dict, Any, List
from src.utils.error_handler import NavigationError
from .selectors import ProductSelectors


class ProductNavigationHandler:
    """Navigation and page management for product scraping"""
    
    def __init__(self, logger):
        self.logger = logger
        self.selectors = ProductSelectors()
    
    def navigate_to_restaurant(self, scraper, restaurant_url: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Navega para a página do restaurante
        
        Args:
            scraper: ProductScraper instance
            restaurant_url: URL of the restaurant to navigate to
            restaurant_name: Name of the restaurant for logging
            
        Returns:
            Dictionary with navigation results
        """
        try:
            self.logger.info(f"Navegando para restaurante: {restaurant_name}")
            self.logger.info(f"URL: {restaurant_url}")
            
            # Navega diretamente para a URL do restaurante
            scraper.page.goto(restaurant_url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento
            scraper.page.wait_for_load_state('networkidle', timeout=20000)
            scraper.wait_with_random_actions(2, 4)
            
            # Verifica se chegou na página correta
            if "delivery" not in scraper.page.url:
                raise NavigationError("Não chegou na página do restaurante")
            
            self.logger.info(f"SUCESSO: Navegação para {restaurant_name} concluída")
            
            return {
                'success': True,
                'restaurant': restaurant_name,
                'url': restaurant_url,
                'final_url': scraper.page.url,
                'message': 'Navegação concluída com sucesso'
            }
            
        except Exception as e:
            error_msg = f"Falha ao navegar para restaurante: {str(e)}"
            self.logger.error(f"ERRO ao navegar para restaurante {restaurant_name}: {str(e)}")
            
            return {
                'success': False,
                'restaurant': restaurant_name,
                'url': restaurant_url,
                'error': error_msg
            }
    
    def wait_for_products_to_load(self, page, timeout: int = 10000) -> bool:
        """
        Aguarda o carregamento dos produtos
        
        Args:
            page: Playwright page object
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if products loaded successfully, False otherwise
        """
        try:
            self.logger.info("Aguardando carregamento dos produtos...")
            
            # Tenta aguardar pelo container de produtos usando XPath
            try:
                page.wait_for_selector(self.selectors.products_list_xpath, timeout=timeout, state="visible")
                self.logger.info("Container de produtos encontrado via XPath")
                return True
            except:
                pass
            
            # Tenta seletores alternativos
            for selector in self.selectors.get_product_selectors():
                try:
                    if page.locator(selector).count() > 0:
                        self.logger.info(f"Produtos encontrados via seletor: {selector}")
                        return True
                except:
                    continue
            
            # Verifica se há mensagem de restaurante fechado
            if self._check_restaurant_closed(page):
                return False
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Erro ao aguardar produtos: {str(e)}")
            return False
    
    def _check_restaurant_closed(self, page) -> bool:
        """
        Verifica se o restaurante está fechado
        
        Args:
            page: Playwright page object
            
        Returns:
            True if restaurant is closed, False otherwise
        """
        try:
            closed_messages = ["fechado", "closed", "não está aceitando pedidos"]
            page_text = page.inner_text("body").lower()
            
            for msg in closed_messages:
                if msg in page_text:
                    self.logger.warning(f"Restaurante fechado: {msg}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Erro ao verificar se restaurante está fechado: {e}")
            return False
    
    def verify_restaurant_page(self, page, restaurant_name: str) -> Dict[str, Any]:
        """
        Verifica se a página do restaurante foi carregada corretamente
        
        Args:
            page: Playwright page object
            restaurant_name: Expected restaurant name
            
        Returns:
            Dictionary with verification results
        """
        verification = {
            'is_valid': False,
            'checks': {},
            'warnings': []
        }
        
        try:
            # Verifica se há container de produtos
            container_exists = False
            for selector in self.selectors.get_container_selectors():
                try:
                    if page.locator(selector).count() > 0:
                        container_exists = True
                        break
                except:
                    continue
            
            verification['checks']['product_container'] = container_exists
            
            # Verifica se há elementos que parecem ser produtos
            product_elements = 0
            for selector in self.selectors.get_primary_selectors():
                try:
                    count = page.locator(selector).count()
                    if count > product_elements:
                        product_elements = count
                except:
                    continue
            
            verification['checks']['product_elements'] = product_elements > 0
            verification['checks']['product_count'] = product_elements
            
            # Verifica se o título da página contém o restaurante
            page_title = page.title()
            restaurant_in_title = restaurant_name.lower() in page_title.lower()
            verification['checks']['restaurant_in_title'] = restaurant_in_title
            
            # Verifica se não há mensagens de erro
            error_messages = page.locator('text="Erro"').count()
            verification['checks']['no_error_messages'] = error_messages == 0
            
            # Verifica se a página não está em loading
            loading_elements = page.locator('[data-testid="loading"], .loading, [class*="loading"]').count()
            verification['checks']['not_loading'] = loading_elements == 0
            
            # Verifica se não está fechado
            is_closed = self._check_restaurant_closed(page)
            verification['checks']['not_closed'] = not is_closed
            
            # Determina se a página é válida
            verification['is_valid'] = (
                container_exists and 
                product_elements > 0 and 
                error_messages == 0 and
                not is_closed
            )
            
            # Adiciona warnings se necessário
            if not restaurant_in_title:
                verification['warnings'].append(f"Título da página não contém '{restaurant_name}'")
            
            if product_elements < 3:
                verification['warnings'].append(f"Poucos produtos encontrados: {product_elements}")
            
            if loading_elements > 0:
                verification['warnings'].append("Elementos de loading ainda visíveis")
            
            if is_closed:
                verification['warnings'].append("Restaurante parece estar fechado")
            
            self.logger.info(f"Verificação da página: {verification}")
            
        except Exception as e:
            self.logger.error(f"Erro na verificação da página: {e}")
            verification['checks']['verification_error'] = str(e)
        
        return verification
    
    def handle_navigation_errors(self, error: Exception, restaurant_name: str) -> Dict[str, Any]:
        """
        Trata erros de navegação e fornece informações úteis
        
        Args:
            error: Exception that occurred during navigation
            restaurant_name: Name of the restaurant being navigated to
            
        Returns:
            Dictionary with error information and suggestions
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'restaurant': restaurant_name,
            'suggestions': []
        }
        
        # Analisa o tipo de erro e fornece sugestões
        if 'timeout' in str(error).lower():
            error_info['suggestions'].extend([
                'Verificar conexão com a internet',
                'Aumentar timeout de navegação',
                'Tentar novamente após alguns segundos'
            ])
        
        elif 'network' in str(error).lower():
            error_info['suggestions'].extend([
                'Verificar conectividade de rede',
                'Verificar se o site está acessível',
                'Tentar com proxy ou VPN'
            ])
        
        elif 'delivery' in str(error).lower():
            error_info['suggestions'].extend([
                'Verificar se a URL do restaurante está correta',
                'Verificar se o restaurante está disponível',
                'Tentar acessar via página principal'
            ])
        
        else:
            error_info['suggestions'].extend([
                'Verificar logs detalhados',
                'Tentar com modo headless desabilitado',
                'Verificar se há captcha ou bloqueios'
            ])
        
        self.logger.error(f"Erro de navegação analisado: {error_info}")
        return error_info
    
    def get_navigation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de navegação"""
        return {
            'default_timeout': 30000,
            'network_timeout': 20000,
            'products_xpath': self.selectors.products_list_xpath,
            'container_selectors': len(self.selectors.get_container_selectors()),
            'product_selectors': len(self.selectors.get_product_selectors()),
            'closed_detection': ['fechado', 'closed', 'não está aceitando pedidos'],
            'verification_checks': [
                'product_container',
                'product_elements',
                'restaurant_in_title',
                'no_error_messages',
                'not_loading',
                'not_closed'
            ]
        }