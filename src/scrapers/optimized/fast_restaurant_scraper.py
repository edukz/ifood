"""
FastRestaurantScraper CORRIGIDO
Baseado exatamente no que funciona no RestaurantScraper original
"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from playwright.async_api import Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from src.scrapers.restaurant_scraper import RestaurantScraper
from src.models.restaurant import Restaurant
from src.utils.helpers import ensure_directories
from src.database.database_adapter import get_database_manager
from src.utils.error_handler import (
    safe_click, safe_fill, validate_page_loaded, 
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)


class FixedFastRestaurantScraper(RestaurantScraper):
    """Versão corrigida do FastRestaurantScraper usando exatamente o que funciona"""
    
    def __init__(self, city: str = None, headless: bool = True):
        super().__init__(city, headless)
        
        # Configurações otimizadas mas funcionais
        self.fast_mode = True
        self.max_scroll_attempts = 3  # Reduzido para ser mais rápido
        self.min_delay = 0.5  # Delays mais rápidos mas seguros
        self.max_delay = 1.5
        
        # USA EXATAMENTE OS SELETORES QUE FUNCIONAM no RestaurantScraper
        self.working_selectors = [
            'a[href*="/delivery/"]',              # ESTE FUNCIONA!
            'div:has(a[href*="delivery"]):has(img)',  # ESTE FUNCIONA!
            'div:has-text("R$"):has(img)',        # ESTE FUNCIONA!
            
            # Outros do RestaurantScraper original
            'div[data-testid="restaurant-card"]',
            'article[data-testid="restaurant"]',
            'li[data-testid="restaurant"]',
            'div[data-testid="store-card"]',
            'div[class*="restaurant-card"]',
            'div[class*="store-card"]',
            'article[class*="restaurant"]',
            'article[class*="store"]',
            'div[role="listitem"]',
            'li[role="listitem"]',
            'article:has(img)',
            'div:has(a[href*="/delivery/"]):has(img)',
            'li:has(img):has-text("R$")',
            'div:has-text("R$"):has(img)',
            'article',
            'li'
        ]
    
    async def navigate_to_category_fast_fixed(self, category_url: str, category_name: str):
        """Navegação CORRIGIDA usando exatamente o fluxo do RestaurantScraper original"""
        self.current_category = category_name
        
        try:
            self.logger.info(f"🔧 Navegação corrigida para: {category_name}")
            
            # USA EXATAMENTE O MESMO FLUXO do RestaurantScraper que funciona
            await self._navigate_full_ifood_flow_async()
            
            # Agora navega para a categoria específica
            self.logger.info(f"🎯 Indo para categoria: {category_url}")
            await self.page.goto(category_url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento completo (mesmo tempo do RestaurantScraper)
            await self.page.wait_for_load_state('networkidle', timeout=20000)
            await asyncio.sleep(2)  # Mesmo delay do original
            
            self.logger.info(f"✅ Navegação corrigida concluída para {category_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na navegação corrigida: {str(e)}")
            raise NavigationError(f"Falha na navegação corrigida: {str(e)}")
    
    async def _navigate_full_ifood_flow_async(self):
        """Conversão async do fluxo EXATO do RestaurantScraper que funciona"""
        try:
            from src.config.settings import SELECTORS
            
            # PASSO 1: Acessar o site (igual ao RestaurantScraper)
            self.logger.info("🏠 Passo 1/5: Acessando https://www.ifood.com.br")
            await self.page.goto("https://www.ifood.com.br", wait_until='domcontentloaded', timeout=30000)
            
            # Valida se a página carregou (igual ao RestaurantScraper)
            current_url = self.page.url
            if "ifood.com.br" not in current_url:
                raise NavigationError("Página do iFood não carregou corretamente")
            
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            await asyncio.sleep(2)  # Mesmo delay do original
            
            # PASSO 2: Preencher cidade (igual ao RestaurantScraper)
            self.logger.info(f"📍 Passo 2/5: Preenchendo cidade: {self.city}")
            
            # Aguarda campo de endereço (igual ao RestaurantScraper)
            try:
                await self.page.wait_for_selector(SELECTORS.address_input, state="visible", timeout=10000)
            except:
                # Fallback com os mesmos seletores do RestaurantScraper
                address_selectors = [
                    'input[placeholder*="endereço"]',
                    'input[placeholder*="Endereço"]',
                    'input[placeholder*="cidade"]',
                    'input[data-testid="address-input"]'
                ]
                found = False
                for selector in address_selectors:
                    if await self.page.locator(selector).count() > 0:
                        SELECTORS.address_input = selector
                        found = True
                        break
                if not found:
                    raise NavigationError("Campo de endereço não encontrado")
            
            # Preenche e confirma (igual ao RestaurantScraper)
            address_input = self.page.locator(SELECTORS.address_input).first
            await address_input.fill(self.city)
            await asyncio.sleep(1)
            await self.page.keyboard.press("Enter")
            
            # Aguarda opções (igual ao RestaurantScraper)
            self.logger.info("Aguardando opções de endereço...")
            await asyncio.sleep(5)  # Mesmo tempo do original
            
            # PASSO 3: Confirmar localização (1/2) (igual ao RestaurantScraper)
            self.logger.info("✅ Passo 3/5: Confirmando localização (1/2)...")
            await asyncio.sleep(1)
            
            try:
                await self.page.locator(SELECTORS.confirm_button_1).click(timeout=10000)
            except:
                # Mesmos fallbacks do RestaurantScraper
                alternative_selectors = [
                    'button:has-text("Confirmar")',
                    'button:has-text("Continuar")',
                    '[data-testid="confirm-button"]',
                    '.confirmation-button'
                ]
                found = False
                for selector in alternative_selectors:
                    try:
                        if await self.page.locator(selector).count() > 0:
                            await self.page.locator(selector).click()
                            found = True
                            break
                    except:
                        continue
                if not found:
                    self.logger.warning("⚠️ Botão de confirmação 1 não encontrado")
            
            # PASSO 4: Confirmar localização (2/2) (igual ao RestaurantScraper)
            await asyncio.sleep(3)  # Mesmo tempo do original
            self.logger.info("✅ Passo 4/5: Confirmando localização (2/2)...")
            
            try:
                await self.page.locator(SELECTORS.confirm_button_2).click(timeout=10000)
            except:
                # Verifica se já está na página correta (igual ao RestaurantScraper)
                current_url = self.page.url
                if "restaurante" in current_url or "delivery" in current_url:
                    self.logger.info("✅ Já está na página de restaurantes")
                else:
                    self.logger.warning("⚠️ Botão de confirmação 2 não encontrado")
            
            # PASSO 5: Acessar seção de restaurantes (igual ao RestaurantScraper)
            await asyncio.sleep(3)  # Mesmo tempo do original
            self.logger.info("🍽️ Passo 5/5: Acessando seção de restaurantes...")
            
            try:
                # Tenta encontrar link para restaurantes (igual ao RestaurantScraper)
                restaurants_selectors = [
                    'a[href*="restaurantes"]',
                    'a:has-text("Restaurantes")',
                    '[data-testid="restaurants-link"]'
                ]
                
                clicked = False
                for selector in restaurants_selectors:
                    try:
                        if await self.page.locator(selector).count() > 0:
                            await self.page.locator(selector).click()
                            clicked = True
                            break
                    except:
                        continue
                
                if clicked:
                    await asyncio.sleep(3)
                    await self.page.wait_for_load_state('networkidle', timeout=15000)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao acessar seção de restaurantes: {e}")
            
            # Resultado final
            final_url = self.page.url
            self.logger.info(f"✅ Navegação iFood concluída: {final_url}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro no fluxo iFood: {str(e)}")
            raise NavigationError(f"Falha no fluxo iFood: {str(e)}")
    
    async def extract_restaurants_fast_fixed(self):
        """Extração CORRIGIDA usando exatamente a lógica que funciona"""
        self.logger.info(f"🔧 Extração corrigida para: {self.current_category}")
        
        try:
            # Aguarda container (igual ao RestaurantScraper)
            self.logger.info("Aguardando container de restaurantes...")
            try:
                await self.page.wait_for_selector(self.restaurants_container_xpath, timeout=15000, state="visible")
            except:
                self.logger.warning("⚠️ Container XPath não encontrado, continuando...")
            
            await asyncio.sleep(1)
            
            # Scroll (igual ao RestaurantScraper mas mais rápido)
            await self._scroll_fast_fixed()
            
            # Extração usando exatamente os seletores que funcionam
            restaurant_elements = []
            successful_selector = None
            
            self.logger.info("🔍 Buscando restaurantes com seletores que funcionam...")
            
            # USA EXATAMENTE A MESMA LÓGICA do RestaurantScraper
            for selector in self.working_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    
                    # Filtra elementos usando EXATAMENTE os critérios do RestaurantScraper
                    valid_elements = []
                    for element in elements:
                        try:
                            text_content = await element.inner_text()
                            text_content = text_content.strip()
                            
                            # EXATAMENTE os critérios do RestaurantScraper
                            is_valid = False
                            
                            # Critério 1: Tem informações típicas de restaurante
                            if (len(text_content) > 10 and 
                                ('R$' in text_content or 'min' in text_content or 
                                 any(word in text_content.lower() for word in ['delivery', 'entrega', 'rating', 'avaliação', 'estrela']))):
                                is_valid = True
                            
                            # Critério 2: Tem link de restaurante ou imagem
                            try:
                                has_restaurant_link = await element.locator('a[href*="/delivery/"], a[href*="/store/"], a[href*="/restaurant/"]').count() > 0
                                has_image = await element.locator('img').count() > 0
                                if has_restaurant_link or (has_image and len(text_content) > 5):
                                    is_valid = True
                            except:
                                pass
                            
                            # Critério 3: Estrutura típica de card de restaurante
                            try:
                                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                                if len(lines) >= 2:
                                    first_line = lines[0]
                                    if len(first_line) > 3 and not first_line.replace('.', '').replace(',', '').isdigit():
                                        is_valid = True
                            except:
                                pass
                            
                            if is_valid:
                                valid_elements.append(element)
                                
                        except Exception as e:
                            continue
                    
                    # Sempre pega o seletor que retorna mais elementos válidos (igual ao RestaurantScraper)
                    if len(valid_elements) > len(restaurant_elements):
                        restaurant_elements = valid_elements
                        successful_selector = selector
                        self.logger.info(f"🎯 Seletor '{selector}': {len(valid_elements)} restaurantes válidos encontrados")
                    
                except Exception as e:
                    continue
            
            if len(restaurant_elements) == 0:
                self.logger.warning("⚠️ Nenhum restaurante encontrado com seletores corrigidos")
                return
            
            self.logger.info(f"✅ SUCESSO: {len(restaurant_elements)} restaurantes encontrados usando '{successful_selector}'")
            
            # Processa restaurantes (igual ao RestaurantScraper mas mais rápido)
            for i, element in enumerate(restaurant_elements, 1):
                try:
                    restaurant_data = await self._extract_restaurant_data_fast_fixed(element, i, len(restaurant_elements))
                    
                    if restaurant_data:
                        restaurant = Restaurant(**restaurant_data)
                        self.restaurants.append(restaurant)
                        self.logger.info(f"✅ SUCESSO [{i}/{len(restaurant_elements)}] {restaurant_data['nome']}")
                    
                    # Delay mínimo entre extrações
                    if i % 10 == 0:
                        await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ ERRO [{i}/{len(restaurant_elements)}] {str(e)[:100]}")
                    continue
            
            self.logger.info(f"🎉 Extração corrigida concluída: {len(self.restaurants)} restaurantes")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração corrigida: {str(e)}")
            raise DataExtractionError(f"Erro na extração corrigida: {str(e)}")
    
    async def _scroll_fast_fixed(self):
        """Scroll corrigido baseado no RestaurantScraper mas mais rápido"""
        try:
            self.logger.info("🔄 Fazendo scroll para carregar restaurantes...")
            
            # Conta inicial (igual ao RestaurantScraper)
            initial_count = await self._count_restaurants_fixed()
            self.logger.info(f"Restaurantes iniciais visíveis: {initial_count}")
            
            # Parâmetros mais rápidos mas eficazes
            last_height = await self.page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 3  # Reduzido para velocidade
            stagnant_attempts = 0
            max_stagnant = 2  # Reduzido para velocidade
            
            while scroll_attempts < max_scrolls and stagnant_attempts < max_stagnant:
                # Scroll em etapas (igual ao RestaurantScraper)
                viewport_height = await self.page.evaluate("window.innerHeight")
                scroll_step = viewport_height * 0.75
                
                for i in range(2):  # Reduzido para velocidade
                    await self.page.evaluate(f"window.scrollBy(0, {scroll_step})")
                    await asyncio.sleep(0.5)  # Mais rápido
                
                await asyncio.sleep(1)  # Aguarda carregamento (mais rápido)
                
                # Verifica mudança
                new_height = await self.page.evaluate("document.body.scrollHeight")
                current_count = await self._count_restaurants_fixed()
                
                if new_height == last_height:
                    stagnant_attempts += 1
                    self.logger.info(f"Altura não mudou (tentativa {stagnant_attempts}/{max_stagnant})")
                    
                    # Estratégia mais agressiva (igual ao RestaurantScraper)
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                    
                    newer_height = await self.page.evaluate("document.body.scrollHeight")
                    if newer_height == new_height:
                        self.logger.info("Nenhuma mudança detectada após estratégia agressiva")
                    else:
                        new_height = newer_height
                        stagnant_attempts = 0
                else:
                    stagnant_attempts = 0
                
                last_height = new_height
                scroll_attempts += 1
                
                self.logger.info(f"Scroll {scroll_attempts}/{max_scrolls} - Altura: {new_height}px - Restaurantes: {current_count}")
            
            final_count = await self._count_restaurants_fixed()
            self.logger.info(f"Scroll finalizado: {final_count} restaurantes carregados (iniciais: {initial_count})")
            
            # Volta ao topo (igual ao RestaurantScraper)
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro durante scroll: {str(e)}")
    
    async def _count_restaurants_fixed(self):
        """Conta restaurantes usando exatamente o método que funciona"""
        try:
            max_count = 0
            
            # Usa os seletores que sabemos que funcionam
            working_selectors = self.working_selectors[:5]  # Primeiros 5 para performance
            
            for selector in working_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    valid_count = 0
                    
                    for element in elements[:100]:  # Limita para performance
                        try:
                            text_content = await element.inner_text()
                            text_content = text_content.strip()
                            
                            # EXATAMENTE os critérios que funcionam
                            if (len(text_content) > 10 and 
                                ('R$' in text_content or 'min' in text_content)):
                                valid_count += 1
                            elif (await element.locator('img').count() > 0 and len(text_content) > 5):
                                valid_count += 1
                                
                        except:
                            continue
                    
                    max_count = max(max_count, valid_count)
                    
                except:
                    continue
            
            return max_count
            
        except:
            return 0
    
    async def _extract_restaurant_data_fast_fixed(self, element, index: int, total: int) -> Optional[Dict[str, Any]]:
        """Extração de dados usando exatamente o método que funciona"""
        try:
            # EXATAMENTE igual ao RestaurantScraper
            full_text = await element.inner_text()
            full_text = full_text.strip()
            
            # Parse do texto (igual ao RestaurantScraper)
            parsed_data = self._parse_restaurant_text(full_text)
            
            if not parsed_data or not parsed_data.get('nome'):
                return None
            
            # Dados básicos (igual ao RestaurantScraper)
            restaurant_data = {
                'nome': parsed_data['nome'],
                'categoria': self.current_category,
                'avaliacao': parsed_data.get('rating', 0.0),
                'distancia': parsed_data.get('distancia', "Não informado"),
                'endereco': "Birigui - SP",
                'cidade': self.city,
                'extracted_at': datetime.now().isoformat()
            }
            
            # URL (igual ao RestaurantScraper)
            url = await self._extract_restaurant_url_async(element)
            restaurant_data['url'] = url
            
            # Tempo e taxa (igual ao RestaurantScraper)
            restaurant_data['tempo_entrega'] = self._extract_delivery_time(full_text)
            restaurant_data['taxa_entrega'] = self._extract_delivery_fee(full_text)
            
            return restaurant_data
            
        except Exception as e:
            return None
    
    async def _extract_restaurant_url_async(self, element) -> Optional[str]:
        """Extração de URL async (baseada no RestaurantScraper)"""
        try:
            # EXATAMENTE os seletores do RestaurantScraper
            url_selectors = [
                'a[href*="/delivery/"]',
                'a[href*="/restaurant/"]',
                'a[href*="/store/"]',
                'a[href]',
                '[data-href]',
                '[onclick*="href"]'
            ]
            
            for selector in url_selectors:
                try:
                    link_element = element.locator(selector).first
                    if await link_element.count() > 0:
                        href = await link_element.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                href = f"https://www.ifood.com.br{href}"
                            return href
                except:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    async def run_fast_for_category_fixed(self, browser, category_url: str, category_name: str):
        """Método principal CORRIGIDO"""
        ensure_directories()
        
        start_time = time.time()
        
        try:
            # Setup
            await self._setup_browser_async(browser)
            
            # Navegação corrigida
            await self.navigate_to_category_fast_fixed(category_url, category_name)
            
            # Extração corrigida
            await self.extract_restaurants_fast_fixed()
            
            # Salva resultado
            save_result = self.save_restaurants()
            
            duration = time.time() - start_time
            
            self.logger.info(f"🎉 EXTRAÇÃO CORRIGIDA CONCLUÍDA em {duration:.1f}s")
            
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
            self.logger.error(f"❌ Erro na extração corrigida ({duration:.1f}s): {e}")
            return {
                'success': False,
                'category': category_name,
                'error': str(e),
                'duration': duration,
                'restaurants_found': 0
            }
            
        finally:
            await self._cleanup_async()
    
    async def _setup_browser_async(self, browser):
        """Setup igual ao original mas garantindo cidade"""
        self.logger.info(f"🔧 Configurando browser corrigido (headless={self.headless})")
        
        if not hasattr(self, 'city') or not self.city:
            self.city = "Birigui"
        
        from src.config.browser_config import BrowserConfig
        
        context_options = BrowserConfig.get_browser_context_options()
        self.browser = browser
        self.context = await self.browser.new_context(**context_options)
        
        # Remove sinais de automação (igual ao original)
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
        """)
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        self.logger.info("✅ Browser corrigido configurado")

    async def _cleanup_async(self):
        """Cleanup async"""
        if hasattr(self, 'context') and self.context:
            try:
                await self.context.close()
            except:
                pass