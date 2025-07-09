#!/usr/bin/env python3
"""
Product Scroll Handler - Lazy loading and scrolling management for product scraping
"""

from typing import Dict, Any, List
from .selectors import ProductSelectors


class ProductScrollHandler:
    """Lazy loading and scrolling management for product scraping"""
    
    def __init__(self, logger, human_simulator):
        self.logger = logger
        self.human = human_simulator
        self.selectors = ProductSelectors()
    
    def scroll_to_load_all_products(self, page) -> Dict[str, Any]:
        """
        Faz scroll agressivo para carregar TODOS os produtos (lazy loading)
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with scroll statistics
        """
        try:
            self.logger.info("Iniciando scroll AGRESSIVO para carregar todos os produtos...")
            
            # Conta produtos iniciais com método específico
            initial_count = self.count_visible_products(page)
            self.logger.info(f"Produtos inicialmente visíveis: {initial_count}")
            
            # Parâmetros de scroll mais agressivos
            scroll_attempts = 0
            max_scrolls = 50  # Muito mais tentativas
            no_change_count = 0
            max_no_change = 5  # Mais tentativas sem mudança
            consecutive_same = 0
            last_count = initial_count
            
            scroll_stats = {
                'initial_count': initial_count,
                'final_count': initial_count,
                'scroll_attempts': 0,
                'no_change_attempts': 0,
                'consecutive_same': 0,
                'strategies_used': [],
                'buttons_clicked': 0
            }
            
            while scroll_attempts < max_scrolls and no_change_count < max_no_change:
                # Conta produtos antes do scroll
                before_count = self.count_visible_products(page)
                
                # Estratégias de scroll mais agressivas
                strategy_used = self.perform_aggressive_scroll(page, scroll_attempts)
                scroll_stats['strategies_used'].append(strategy_used)
                
                # Aguarda carregamento com tempo variável
                wait_time = 1.0 if scroll_attempts < 10 else 2.0
                self.human.random_delay(wait_time, wait_time + 1.0)
                
                # Conta produtos após scroll
                after_count = self.count_visible_products(page)
                
                if after_count > before_count:
                    self.logger.info(f"Scroll {scroll_attempts + 1}: {before_count} → {after_count} produtos (+{after_count - before_count})")
                    no_change_count = 0  # Reset contador
                    consecutive_same = 0
                elif after_count == last_count:
                    consecutive_same += 1
                    no_change_count += 1
                    self.logger.info(f"Scroll {scroll_attempts + 1}: Estagnado em {after_count} produtos ({consecutive_same} consecutivos)")
                else:
                    no_change_count += 1
                    self.logger.info(f"Scroll {scroll_attempts + 1}: {before_count} → {after_count} ({no_change_count}/{max_no_change})")
                
                last_count = after_count
                scroll_attempts += 1
                
                # Força aguarda extra se estiver estagnado
                if consecutive_same >= 2:
                    self.logger.info("Estagnação detectada, aguardando carregamento extra...")
                    self.human.random_delay(3, 5)
                    # Tenta scroll forçado
                    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    self.human.random_delay(2, 3)
            
            final_count = self.count_visible_products(page)
            self.logger.info(f"Scroll AGRESSIVO concluído: {initial_count} → {final_count} produtos (+{final_count - initial_count})")
            
            # Volta ao topo gradualmente para extração
            page.evaluate("window.scrollTo(0, 0)")
            self.human.random_delay(3, 4)
            
            # Update final stats
            scroll_stats.update({
                'final_count': final_count,
                'scroll_attempts': scroll_attempts,
                'no_change_attempts': no_change_count,
                'consecutive_same': consecutive_same,
                'products_loaded': final_count - initial_count
            })
            
            return scroll_stats
            
        except Exception as e:
            self.logger.warning(f"Erro durante scroll agressivo: {str(e)}")
            return {
                'initial_count': 0,
                'final_count': 0,
                'scroll_attempts': 0,
                'error': str(e)
            }
    
    def perform_aggressive_scroll(self, page, attempt: int) -> str:
        """
        Executa scroll mais agressivo para garantir carregamento completo
        
        Args:
            page: Playwright page object
            attempt: Current scroll attempt number
            
        Returns:
            String describing the strategy used
        """
        try:
            scroll_strategy = attempt % 6
            strategy_name = ""
            
            if scroll_strategy == 0:
                # Scroll até o final absoluto
                page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                strategy_name = "scroll_to_bottom"
            elif scroll_strategy == 1:
                # Scroll por viewport completo
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                strategy_name = "scroll_by_viewport"
            elif scroll_strategy == 2:
                # Scroll por viewport duplo
                page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
                strategy_name = "scroll_by_double_viewport"
            elif scroll_strategy == 3:
                # Scroll por percentual da página
                page.evaluate("window.scrollBy(0, document.documentElement.scrollHeight * 0.3)")
                strategy_name = "scroll_by_percentage"
            elif scroll_strategy == 4:
                # Scroll gradual lento
                page.evaluate("window.scrollBy(0, window.innerHeight * 0.5)")
                strategy_name = "scroll_gradual"
            else:
                # Scroll até meio da página
                page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight / 2)")
                strategy_name = "scroll_to_middle"
            
            # A cada 10 tentativas, força interação com containers
            if attempt % 10 == 0:
                buttons_clicked = self._try_load_more_buttons(page)
                self._try_container_interactions(page)
                if buttons_clicked > 0:
                    strategy_name += f"_with_{buttons_clicked}_buttons"
            
            return strategy_name
                    
        except Exception as e:
            self.logger.debug(f"Erro no scroll agressivo estratégia {attempt}: {str(e)}")
            return f"error_{attempt}"
    
    def _try_load_more_buttons(self, page) -> int:
        """Tenta clicar em botões 'Ver mais' ou similares"""
        buttons_clicked = 0
        
        try:
            # Tenta clicar em botões "Ver mais" ou similares
            more_buttons = page.locator('button:has-text("Ver mais"), button:has-text("Carregar mais"), button:has-text("Mostrar mais")').all()
            for button in more_buttons[:3]:  # Máximo 3 botões
                try:
                    if button.is_visible():
                        button.click()
                        self.human.random_delay(1, 2)
                        self.logger.info("Clicou em botão 'Ver mais'")
                        buttons_clicked += 1
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Erro ao tentar clicar em botões: {e}")
        
        return buttons_clicked
    
    def _try_container_interactions(self, page):
        """Tenta scroll em containers específicos"""
        try:
            # Tenta scroll em containers específicos
            for container_selector in self.selectors.get_container_selectors():
                try:
                    container = page.locator(container_selector).first
                    if container.count() > 0:
                        container.scroll_into_view_if_needed()
                        break
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Erro nas interações com containers: {e}")
    
    def count_visible_products(self, page) -> int:
        """
        Conta produtos visíveis usando seletores mais específicos
        
        Args:
            page: Playwright page object
            
        Returns:
            Number of visible products
        """
        counts = {}
        
        # Seletores mais específicos para contagem real de produtos
        specific_selectors = [
            self.selectors.product_item_xpath,  # XPath original
            'li[data-testid="dish-card"]',
            'div[data-testid="menu-item"]', 
            'article[data-testid="product"]',
            'div[class*="dish-card"]',
            'li:has-text("R$")',  # Elementos com preço
        ]
        
        for selector in specific_selectors:
            try:
                count = page.locator(selector).count()
                if count > 0:
                    counts[selector] = count
                    self.logger.debug(f"Contador {selector}: {count} elementos")
            except:
                continue
        
        if counts:
            # Retorna a contagem do seletor que encontrou mais produtos válidos
            best_selector = max(counts, key=counts.get)
            best_count = counts[best_selector]
            self.logger.debug(f"Melhor seletor para contagem: {best_selector} ({best_count} produtos)")
            return best_count
        
        return 0
    
    def perform_smart_scroll(self, page, attempt: int) -> str:
        """
        Executa diferentes estratégias de scroll baseado na tentativa
        
        Args:
            page: Playwright page object
            attempt: Current scroll attempt number
            
        Returns:
            String describing the strategy used
        """
        try:
            strategy_name = ""
            
            if attempt % 4 == 0:
                # Scroll até o final da página
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                strategy_name = "smart_scroll_to_bottom"
            elif attempt % 4 == 1:
                # Scroll gradual por viewport
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                strategy_name = "smart_scroll_by_viewport"
            elif attempt % 4 == 2:
                # Scroll médio
                page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                strategy_name = "smart_scroll_medium"
            else:
                # Scroll por seções (útil para menus categorizados)
                page.evaluate("window.scrollBy(0, window.innerHeight * 0.7)")
                strategy_name = "smart_scroll_sections"
            
            # A cada 5 tentativas, tenta scroll em elementos específicos
            if attempt % 5 == 0:
                self._try_element_specific_scroll(page)
                strategy_name += "_with_elements"
            
            return strategy_name
                    
        except Exception as e:
            self.logger.debug(f"Erro no scroll inteligente: {str(e)}")
            return f"smart_error_{attempt}"
    
    def _try_element_specific_scroll(self, page):
        """Tenta scroll em elementos específicos"""
        try:
            # Tenta scroll em produtos específicos
            for selector in self.selectors.get_primary_selectors():
                try:
                    elements = page.locator(selector).all()
                    if elements and len(elements) > 0:
                        # Scroll para o último elemento visível
                        last_element = elements[-1]
                        last_element.scroll_into_view_if_needed()
                        break
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Erro no scroll específico de elementos: {e}")
    
    def get_scroll_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de scroll formatadas"""
        return {
            'strategies': [
                'scroll_to_bottom',
                'scroll_by_viewport', 
                'scroll_by_double_viewport',
                'scroll_by_percentage',
                'scroll_gradual',
                'scroll_to_middle'
            ],
            'smart_strategies': [
                'smart_scroll_to_bottom',
                'smart_scroll_by_viewport',
                'smart_scroll_medium',
                'smart_scroll_sections'
            ],
            'max_scrolls': 50,
            'max_no_change': 5,
            'interaction_frequency': 10,  # A cada 10 scrolls
            'smart_interaction_frequency': 5,  # A cada 5 scrolls
            'supported_buttons': ['Ver mais', 'Carregar mais', 'Mostrar mais'],
            'counting_selectors': 6
        }