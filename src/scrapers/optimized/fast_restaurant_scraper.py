"""
RestaurantScraper ULTRA-OTIMIZADO
Reduz tempo de extração de 5 minutos para 1 minuto por categoria
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from playwright.sync_api import Playwright, TimeoutError, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from src.scrapers.restaurant_scraper import RestaurantScraper
from src.models.restaurant import Restaurant
from src.utils.helpers import ensure_directories
from src.utils.database import DatabaseManager
from src.utils.error_handler import (
    safe_click, safe_fill, validate_page_loaded, 
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)


class FastRestaurantScraper(RestaurantScraper):
    """Versão ultra-otimizada do RestaurantScraper"""
    
    def __init__(self, city: str = None, headless: bool = True):
        super().__init__(city, headless)
        
        # Configurações otimizadas
        self.fast_mode = True
        self.max_scroll_attempts = 8  # vs 25 original
        self.min_delay = 0.3  # vs 2-5s original
        self.max_delay = 1.0  # vs 2-5s original
        
        # Seletores otimizados (apenas os mais eficazes)
        self.fast_selectors = [
            'div[data-testid="restaurant-card"]',
            'article[data-testid="restaurant"]',
            'a[href*="/delivery/"]',
            'div[class*="restaurant-card"]',
            'article:has(img)',
        ]
    
    def navigate_to_category_fast(self, category_url: str, category_name: str):
        """Navegação ULTRA-RÁPIDA - vai direto para a categoria"""
        self.current_category = category_name
        
        try:
            self.logger.info(f"⚡ Navegação rápida para: {category_name}")
            
            # VAI DIRETO PARA A URL DA CATEGORIA (sem passar pela home)
            self.logger.info(f"🚀 Indo direto para: {category_url}")
            self.page.goto(category_url, wait_until='domcontentloaded', timeout=20000)
            
            # Delay mínimo para carregamento
            time.sleep(1)
            
            # Verifica se precisa preencher cidade (às vezes aparece popup)
            try:
                # Se aparecer popup de localização, preenche rapidamente
                if self.page.locator('input[placeholder*="endereço"], input[placeholder*="cidade"]').count() > 0:
                    self.logger.info("⚡ Preenchendo localização rápida...")
                    address_input = self.page.locator('input[placeholder*="endereço"], input[placeholder*="cidade"]').first
                    address_input.fill(self.city)
                    time.sleep(0.5)
                    self.page.keyboard.press("Enter")
                    time.sleep(2)
            except:
                pass
            
            # Aguarda carregamento mínimo
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(1)
            
            self.logger.info(f"✅ Navegação rápida concluída para {category_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na navegação rápida: {str(e)}")
            raise NavigationError(f"Falha na navegação rápida: {str(e)}")
    
    def _scroll_fast(self):
        """Scroll ULTRA-OTIMIZADO - 3x mais rápido"""
        try:
            self.logger.info("⚡ Scroll rápido iniciado...")
            
            last_height = self.page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            stagnant_count = 0
            
            while scroll_attempts < self.max_scroll_attempts and stagnant_count < 3:
                # Scroll mais agressivo e rápido
                self.page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                time.sleep(self.min_delay)  # 0.3s vs 2-3s original
                
                new_height = self.page.evaluate("document.body.scrollHeight")
                
                if new_height == last_height:
                    stagnant_count += 1
                    # Scroll final rápido
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(self.max_delay)  # 1s vs 3-5s original
                else:
                    stagnant_count = 0
                
                last_height = new_height
                scroll_attempts += 1
                
                # Log apenas a cada 3 tentativas
                if scroll_attempts % 3 == 0:
                    self.logger.info(f"⚡ Scroll {scroll_attempts}/{self.max_scroll_attempts}")
            
            # Volta ao topo rapidamente
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)  # vs 2-3s original
            
            self.logger.info(f"✅ Scroll rápido concluído em {scroll_attempts} tentativas")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro no scroll rápido: {str(e)}")
    
    def _extract_fast(self):
        """Extração ULTRA-OTIMIZADA - usa apenas seletores eficazes"""
        self.logger.info("⚡ Extração rápida iniciada...")
        
        best_elements = []
        best_selector = None
        
        # Testa apenas os seletores mais eficazes
        for selector in self.fast_selectors:
            try:
                elements = self.page.locator(selector).all()
                
                if len(elements) > len(best_elements):
                    # Validação rápida - apenas critérios básicos
                    valid_elements = []
                    for element in elements[:50]:  # Limita para performance
                        try:
                            text = element.inner_text(timeout=1000).strip()  # Timeout curto
                            if len(text) > 15 and ('R$' in text or 'min' in text):
                                valid_elements.append(element)
                        except:
                            continue
                    
                    if len(valid_elements) > len(best_elements):
                        best_elements = valid_elements
                        best_selector = selector
                        self.logger.info(f"⚡ Seletor '{selector}': {len(valid_elements)} elementos")
                        
                        # Para no primeiro seletor bom (vs testar todos)
                        if len(valid_elements) > 10:
                            break
                
            except Exception as e:
                self.logger.debug(f"Seletor '{selector}' falhou: {str(e)}")
                continue
        
        self.logger.info(f"✅ Melhor seletor: '{best_selector}' com {len(best_elements)} elementos")
        return best_elements, best_selector
    
    def _extract_restaurant_data_fast(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extração rápida de dados - apenas essenciais"""
        try:
            # Extração mínima e rápida
            text = element.inner_text(timeout=1000).strip()
            
            if len(text) < 10:
                return None
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) < 2:
                return None
            
            # Parse rápido - apenas dados essenciais
            restaurant_data = {
                'nome': lines[0],
                'categoria': self.current_category,
                'avaliacao': self._extract_rating_fast(text),
                'tempo_entrega': self._extract_time_fast(text),
                'taxa_entrega': self._extract_fee_fast(text),
                'distancia': self._extract_distance_fast(text),
                'endereco': "Birigui - SP",  # Fixo para velocidade
                'url': self._extract_url_fast(element),
                'cidade': self.city,
                'extracted_at': datetime.now().isoformat()
            }
            
            return restaurant_data
            
        except Exception as e:
            self.logger.debug(f"Erro rápido elemento {index}: {str(e)}")
            return None
    
    def _extract_rating_fast(self, text: str) -> float:
        """Extração rápida de rating"""
        import re
        match = re.search(r'(\d+[.,]\d+)', text)
        if match:
            try:
                rating = float(match.group(1).replace(',', '.'))
                if 0 <= rating <= 5:
                    return rating
            except:
                pass
        return 0.0
    
    def _extract_time_fast(self, text: str) -> str:
        """Extração rápida de tempo"""
        import re
        match = re.search(r'(\d+-\d+\s*min|\d+\s*min)', text, re.IGNORECASE)
        return match.group(1) if match else "Não informado"
    
    def _extract_fee_fast(self, text: str) -> str:
        """Extração rápida de taxa"""
        import re
        if 'grátis' in text.lower():
            return "Grátis"
        match = re.search(r'(R\$\s*\d+[.,]?\d*)', text)
        return match.group(1) if match else "Não informado"
    
    def _extract_distance_fast(self, text: str) -> str:
        """Extração rápida de distância"""
        import re
        match = re.search(r'(\d+[.,]?\d*\s*km)', text, re.IGNORECASE)
        return match.group(1) if match else "Não informado"
    
    def _extract_url_fast(self, element) -> str:
        """Extração rápida de URL"""
        try:
            # Apenas tenta o mais comum
            link = element.locator('a[href*="/delivery/"]').first
            if link.count() > 0:
                href = link.get_attribute('href', timeout=1000)
                if href and href.startswith('/'):
                    return f"https://www.ifood.com.br{href}"
                return href or ""
        except:
            pass
        return ""
    
    def extract_restaurants_fast(self):
        """Método principal ULTRA-OTIMIZADO"""
        self.logger.info(f"⚡ Extração rápida para: {self.current_category}")
        
        try:
            # 1. Aguarda container básico (timeout reduzido)
            try:
                self.page.wait_for_selector('main, article, [data-testid]', timeout=10000, state="visible")
            except TimeoutError:
                self.logger.warning("⚠️ Container não encontrado, continuando...")
            
            # 2. Scroll rápido
            self._scroll_fast()
            
            # 3. Extração rápida
            restaurant_elements, successful_selector = self._extract_fast()
            
            if not restaurant_elements:
                self.logger.warning("⚠️ Nenhum restaurante encontrado")
                return
            
            # 4. Processamento rápido
            self.logger.info(f"⚡ Processando {len(restaurant_elements)} restaurantes...")
            
            for i, element in enumerate(restaurant_elements):
                try:
                    restaurant_data = self._extract_restaurant_data_fast(element, i)
                    
                    if restaurant_data:
                        restaurant = Restaurant(**restaurant_data)
                        self.restaurants.append(restaurant)
                        
                        # Log apenas a cada 20 elementos
                        if i % 20 == 0:
                            self.logger.info(f"⚡ Processado {i}/{len(restaurant_elements)}")
                    
                    # Delay mínimo entre elementos
                    if i % 10 == 0:  # Delay apenas a cada 10 elementos
                        time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.debug(f"Erro elemento {i}: {str(e)}")
                    continue
            
            self.logger.info(f"✅ Extração rápida concluída: {len(self.restaurants)} restaurantes")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração rápida: {str(e)}")
            raise DataExtractionError(f"Erro na extração rápida: {str(e)}")
    
    def run_fast_for_category(self, playwright: Playwright, category_url: str, category_name: str):
        """Método principal ULTRA-RÁPIDO"""
        ensure_directories()
        
        start_time = time.time()
        
        try:
            self.setup_browser(playwright)
            self.navigate_to_category_fast(category_url, category_name)
            self.extract_restaurants_fast()
            save_result = self.save_restaurants()
            
            duration = time.time() - start_time
            
            self.logger.info(f"⚡ EXTRAÇÃO RÁPIDA CONCLUÍDA em {duration:.1f}s")
            
            return {
                'success': True,
                'category': category_name,
                'restaurants_found': len(self.restaurants),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'total_in_db': save_result['total'],
                'duration': duration,
                'restaurants': self.restaurants
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"❌ Erro na extração rápida ({duration:.1f}s): {e}")
            return {
                'success': False,
                'category': category_name,
                'error': str(e),
                'duration': duration,
                'restaurants_found': 0
            }
            
        finally:
            self.cleanup()