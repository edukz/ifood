#!/usr/bin/env python3
"""
Scroll Handler - Lazy loading and scrolling management for restaurant scraping
"""

from typing import Dict, Any
from .selectors import RestaurantSelectors


class ScrollHandler:
    """Lazy loading and scrolling management for restaurant scraping"""
    
    def __init__(self, logger, human_simulator):
        self.logger = logger
        self.human = human_simulator
        self.selectors = RestaurantSelectors()
    
    def scroll_to_load_restaurants(self, page, element_counter) -> Dict[str, Any]:
        """
        Faz scroll para carregar mais restaurantes (lazy loading) - versão otimizada
        
        Args:
            page: Playwright page object
            element_counter: Function to count elements on page
            
        Returns:
            Dictionary with scroll statistics
        """
        try:
            self.logger.info("Iniciando scroll progressivo para carregar TODOS os restaurantes...")
            
            # Configurações mais agressivas para capturar mais restaurantes
            last_height = page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 25  # Aumentado para capturar mais
            stagnant_attempts = 0
            max_stagnant = 3  # Máximo de tentativas sem mudança
            
            # Conta inicial de restaurantes
            initial_count = element_counter()
            self.logger.info(f"Restaurantes iniciais visíveis: {initial_count}")
            
            scroll_stats = {
                'initial_count': initial_count,
                'final_count': initial_count,
                'scroll_attempts': 0,
                'buttons_clicked': 0,
                'height_changes': 0
            }
            
            while scroll_attempts < max_scrolls and stagnant_attempts < max_stagnant:
                # Scroll em etapas menores para trigger lazy loading
                scroll_stats['scroll_attempts'] += 1
                scroll_attempts += 1
                
                self._perform_scroll_step(page)
                
                # Verifica se há mais conteúdo
                new_height = page.evaluate("document.body.scrollHeight")
                current_count = element_counter()
                
                if new_height == last_height:
                    stagnant_attempts += 1
                    self.logger.info(f"Altura não mudou (tentativa {stagnant_attempts}/{max_stagnant})")
                    
                    # Estratégia mais agressiva quando não há mudança
                    if self._try_aggressive_scroll(page):
                        # Verifica novamente após estratégia agressiva
                        newer_height = page.evaluate("document.body.scrollHeight")
                        newer_count = element_counter()
                        
                        if newer_height != new_height or newer_count != current_count:
                            new_height = newer_height
                            current_count = newer_count
                            stagnant_attempts = 0  # Reset contador
                            scroll_stats['height_changes'] += 1
                else:
                    stagnant_attempts = 0  # Reset contador quando há progresso
                    scroll_stats['height_changes'] += 1
                
                last_height = new_height
                
                self.logger.info(f"Scroll {scroll_attempts}/{max_scrolls} - Altura: {new_height}px - Restaurantes: {current_count}")
                
                # Estratégias extras a partir do 10º scroll
                if scroll_attempts > 10:
                    buttons_clicked = self._try_load_more_buttons(page)
                    scroll_stats['buttons_clicked'] += buttons_clicked
                
                # Estratégia de scroll infinito - simula chegada próxima ao final
                if scroll_attempts > 5:
                    self._try_infinite_scroll(page)
            
            # Log final
            final_count = element_counter()
            scroll_stats['final_count'] = final_count
            self.logger.info(f"Scroll finalizado: {final_count} restaurantes carregados (iniciais: {initial_count})")
            
            # Volta ao topo para começar extração
            page.evaluate("window.scrollTo(0, 0)")
            self.human.random_delay(2, 3)
            self.logger.info("Voltando ao topo para iniciar extração...")
            
            return scroll_stats
            
        except Exception as e:
            self.logger.warning(f"AVISO: Erro durante scroll: {str(e)}")
            return {
                'initial_count': 0,
                'final_count': 0,
                'scroll_attempts': 0,
                'buttons_clicked': 0,
                'height_changes': 0,
                'error': str(e)
            }
    
    def _perform_scroll_step(self, page):
        """Executa uma etapa de scroll com timing otimizado"""
        try:
            viewport_height = page.evaluate("window.innerHeight")
            scroll_step = viewport_height * 0.75  # 75% da altura da viewport
            
            # Faz múltiplos scrolls pequenos
            for i in range(3):
                page.evaluate(f"window.scrollBy(0, {scroll_step})")
                self.human.random_delay(0.8, 1.2)
            
            # Pausa maior para permitir carregamento
            self.human.random_delay(2, 3)
            
        except Exception as e:
            self.logger.debug(f"Erro no scroll step: {e}")
    
    def _try_aggressive_scroll(self, page) -> bool:
        """Tenta estratégia agressiva de scroll quando não há mudança"""
        try:
            # Simula scroll até o final da página
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.human.random_delay(3, 5)
            
            # Tenta trigger manual de lazy loading
            page.evaluate("""
                // Trigger eventos que podem ativar lazy loading
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
                
                // Força reflow
                document.body.offsetHeight;
            """)
            self.human.random_delay(2, 3)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erro na estratégia agressiva: {e}")
            return False
    
    def _try_load_more_buttons(self, page) -> int:
        """Tenta clicar em botões 'Ver mais' ou similares"""
        buttons_clicked = 0
        
        try:
            for selector in self.selectors.get_load_more_selectors():
                try:
                    elements = page.locator(selector)
                    if elements.count() > 0:
                        # Verifica se o botão está visível e habilitado
                        for i in range(elements.count()):
                            element = elements.nth(i)
                            if element.is_visible() and element.is_enabled():
                                self.logger.info(f"Clicando em botão 'Ver mais': {selector}")
                                element.scroll_into_view_if_needed()
                                self.human.random_delay(1, 2)
                                element.click()
                                self.human.random_delay(4, 6)
                                buttons_clicked += 1
                                break
                        if buttons_clicked > 0:
                            break
                except Exception as e:
                    self.logger.debug(f"Erro ao tentar clicar em {selector}: {e}")
                    continue
            
            if buttons_clicked > 0:
                # Aguarda carregamento após click
                self.human.random_delay(3, 5)
                
        except Exception as e:
            self.logger.debug(f"Erro na busca por botões: {e}")
        
        return buttons_clicked
    
    def _try_infinite_scroll(self, page):
        """Tenta estratégia de scroll infinito"""
        try:
            # Simula scroll até quase o final da página
            page.evaluate("""
                const scrollHeight = document.body.scrollHeight;
                const viewportHeight = window.innerHeight;
                const scrollPosition = scrollHeight - viewportHeight - 100;
                window.scrollTo(0, scrollPosition);
            """)
            self.human.random_delay(2, 3)
            
        except Exception as e:
            self.logger.debug(f"Erro no scroll infinito: {e}")
    
    def get_scroll_statistics(self) -> Dict[str, str]:
        """Retorna estatísticas de scroll formatadas"""
        return {
            'status': 'Module loaded successfully',
            'strategies': 'Progressive, Aggressive, Load More Buttons, Infinite Scroll',
            'max_scrolls': '25',
            'max_stagnant': '3'
        }