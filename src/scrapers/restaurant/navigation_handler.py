#!/usr/bin/env python3
"""
Navigation Handler - Navigation and page management for restaurant scraping
"""

from typing import Dict, Any
from src.utils.error_handler import NavigationError


class NavigationHandler:
    """Navigation and page management for restaurant scraping"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def navigate_to_category(self, scraper, category_url: str, category_name: str) -> Dict[str, Any]:
        """
        Navega para uma categoria específica usando o fluxo padrão do iFood
        
        Args:
            scraper: RestaurantScraper instance
            category_url: URL of the category to navigate to
            category_name: Name of the category for logging
            
        Returns:
            Dictionary with navigation results
        """
        try:
            self.logger.info(f"Navegando para categoria: {category_name}")
            self.logger.info("Usando navegação padrão do iFood (com preenchimento de cidade)")
            
            # Usa a navegação padrão do IfoodScraper (mesmo fluxo que CategoryScraper)
            scraper.navigate()
            
            # Agora navega para a categoria específica
            self.logger.info(f"Navegando para URL da categoria: {category_url}")
            scraper.page.goto(category_url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento completo
            scraper.page.wait_for_load_state('networkidle', timeout=20000)
            scraper.wait_with_random_actions(2, 4)
            
            self.logger.info(f"SUCESSO: Navegação para {category_name} concluída")
            
            return {
                'success': True,
                'category': category_name,
                'url': category_url,
                'message': 'Navegação concluída com sucesso'
            }
            
        except Exception as e:
            error_msg = f"Falha ao navegar para categoria {category_name}: {str(e)}"
            self.logger.error(f"ERRO ao navegar para categoria {category_name}: {str(e)}")
            
            return {
                'success': False,
                'category': category_name,
                'url': category_url,
                'error': error_msg
            }
    
    def wait_for_page_load(self, page, timeout: int = 15000) -> bool:
        """
        Aguarda carregamento completo da página
        
        Args:
            page: Playwright page object
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if page loaded successfully, False otherwise
        """
        try:
            # Aguarda o container de restaurantes aparecer
            containers_xpath = '//*[@id="__next"]/div[1]/main/div/section/article'
            page.wait_for_selector(containers_xpath, timeout=timeout, state="visible")
            
            # Aguarda rede ficar idle
            page.wait_for_load_state('networkidle', timeout=timeout)
            
            self.logger.info("Página carregada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao aguardar carregamento da página: {e}")
            return False
    
    def handle_navigation_errors(self, error: Exception, category_name: str) -> Dict[str, Any]:
        """
        Trata erros de navegação e fornece informações úteis
        
        Args:
            error: Exception that occurred during navigation
            category_name: Name of the category being navigated to
            
        Returns:
            Dictionary with error information and suggestions
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category_name,
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
        
        elif 'selector' in str(error).lower():
            error_info['suggestions'].extend([
                'Verificar se a estrutura da página mudou',
                'Atualizar seletores CSS',
                'Verificar se há elementos de loading'
            ])
        
        else:
            error_info['suggestions'].extend([
                'Verificar logs detalhados',
                'Tentar com modo headless desabilitado',
                'Verificar se há captcha ou bloqueios'
            ])
        
        self.logger.error(f"Erro de navegação analisado: {error_info}")
        return error_info
    
    def verify_category_page(self, page, category_name: str) -> Dict[str, Any]:
        """
        Verifica se a página da categoria foi carregada corretamente
        
        Args:
            page: Playwright page object
            category_name: Expected category name
            
        Returns:
            Dictionary with verification results
        """
        verification = {
            'is_valid': False,
            'checks': {},
            'warnings': []
        }
        
        try:
            # Verifica se há container de restaurantes
            container_exists = page.locator('//*[@id="__next"]/div[1]/main/div/section/article').count() > 0
            verification['checks']['restaurant_container'] = container_exists
            
            # Verifica se há elementos que parecem ser restaurantes
            restaurant_elements = page.locator('div[data-testid="restaurant-card"]').count()
            verification['checks']['restaurant_elements'] = restaurant_elements > 0
            verification['checks']['restaurant_count'] = restaurant_elements
            
            # Verifica se o título da página contém a categoria
            page_title = page.title()
            category_in_title = category_name.lower() in page_title.lower()
            verification['checks']['category_in_title'] = category_in_title
            
            # Verifica se não há mensagens de erro
            error_messages = page.locator('text="Erro"').count()
            verification['checks']['no_error_messages'] = error_messages == 0
            
            # Verifica se a página não está em loading
            loading_elements = page.locator('[data-testid="loading"], .loading, [class*="loading"]').count()
            verification['checks']['not_loading'] = loading_elements == 0
            
            # Determina se a página é válida
            verification['is_valid'] = (
                container_exists and 
                restaurant_elements > 0 and 
                error_messages == 0
            )
            
            # Adiciona warnings se necessário
            if not category_in_title:
                verification['warnings'].append(f"Título da página não contém '{category_name}'")
            
            if restaurant_elements < 5:
                verification['warnings'].append(f"Poucos restaurantes encontrados: {restaurant_elements}")
            
            if loading_elements > 0:
                verification['warnings'].append("Elementos de loading ainda visíveis")
            
            self.logger.info(f"Verificação da página: {verification}")
            
        except Exception as e:
            self.logger.error(f"Erro na verificação da página: {e}")
            verification['checks']['verification_error'] = str(e)
        
        return verification
    
    def get_navigation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de navegação"""
        return {
            'default_timeout': 30000,
            'network_timeout': 20000,
            'container_xpath': '//*[@id="__next"]/div[1]/main/div/section/article',
            'supported_wait_states': ['domcontentloaded', 'networkidle'],
            'error_handling': ['timeout', 'network', 'selector'],
            'verification_checks': [
                'restaurant_container',
                'restaurant_elements', 
                'category_in_title',
                'no_error_messages',
                'not_loading'
            ]
        }