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
from src.utils.database import DatabaseManager
from src.utils.error_handler import (
    safe_click, safe_fill, validate_page_loaded, 
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)
from src.config.settings import SETTINGS


class RestaurantScraper(IfoodScraper):
    """Scraper específico para extrair dados dos restaurantes"""
    
    def __init__(self, city: str = None, headless: bool = False):
        super().__init__(city, headless)
        self.restaurants: List[Restaurant] = []
        self.restaurants_container_xpath = '//*[@id="__next"]/div[1]/main/div/section/article'
        # Seletores otimizados para capturar mais restaurantes
        self.restaurant_selectors = [
            # Seletores específicos do iFood
            'div[data-testid="restaurant-card"]',
            'article[data-testid="restaurant"]',
            'li[data-testid="restaurant"]',
            'div[data-testid="store-card"]',
            '[data-testid*="restaurant"]',
            '[data-testid*="store"]',
            
            # Seletores por links
            'a[href*="/delivery/"]',
            'a[href*="/store/"]', 
            'a[href*="/restaurant/"]',
            
            # Seletores por classes
            'div[class*="restaurant-card"]',
            'div[class*="store-card"]',
            'article[class*="restaurant"]',
            'article[class*="store"]',
            '[class*="restaurant-item"]',
            '[class*="store-item"]',
            
            # Seletores por estrutura
            'div[role="listitem"]',
            'li[role="listitem"]',
            
            # Seletores mais amplos (ordenados por especificidade)
            'article:has(img)',  # Artigos com imagens
            'div:has(a[href*="delivery"]):has(img)',  # Divs com links de delivery e imagens
            'li:has(img):has-text("R$")',  # Items de lista com imagem e preço
            'div:has-text("R$"):has(img)',  # Divs com preço e imagem
            
            # Fallbacks mais genéricos
            'article',
            'li'
        ]
        self.db = DatabaseManager()
        self.current_category = None
    
    def navigate_to_category(self, category_url: str, category_name: str):
        """Navega para uma categoria específica usando o fluxo padrão do iFood"""
        self.current_category = category_name
        
        try:
            self.logger.info(f"Navegando para categoria: {category_name}")
            self.logger.info("Usando navegação padrão do iFood (com preenchimento de cidade)")
            
            # Usa a navegação padrão do IfoodScraper (mesmo fluxo que CategoryScraper)
            self.navigate()
            
            # Agora navega para a categoria específica
            self.logger.info(f"Navegando para URL da categoria: {category_url}")
            self.page.goto(category_url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento completo
            self.page.wait_for_load_state('networkidle', timeout=20000)
            self.wait_with_random_actions(2, 4)
            
            self.logger.info(f"SUCESSO: Navegação para {category_name} concluída")
            
        except Exception as e:
            self.logger.error(f"ERRO ao navegar para categoria {category_name}: {str(e)}")
            raise NavigationError(f"Falha ao navegar para categoria {category_name}: {str(e)}")
    
    
    @with_retry(max_attempts=2, delay=3.0)
    def extract_restaurants(self):
        """Extrai dados dos restaurantes da categoria atual"""
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
            
            # Scroll para carregar mais restaurantes
            self.logger.info("Fazendo scroll para carregar restaurantes...")
            self._scroll_to_load_restaurants()
            
            # Busca todos os elementos de restaurantes usando múltiplos seletores
            restaurant_elements = []
            successful_selector = None
            
            self.logger.info("Buscando restaurantes com diferentes seletores...")
            
            for selector in self.restaurant_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    
                    # Filtra elementos que realmente parecem ser restaurantes
                    valid_elements = []
                    for element in elements:
                        try:
                            # Verifica se o elemento tem conteúdo de texto relevante
                            text_content = element.inner_text().strip()
                            
                            # Critérios mais flexíveis para validação
                            is_valid = False
                            
                            # Critério 1: Tem informações típicas de restaurante
                            if (len(text_content) > 10 and 
                                ('R$' in text_content or 'min' in text_content or 
                                 any(word in text_content.lower() for word in ['delivery', 'entrega', 'rating', 'avaliação', 'estrela']))):
                                is_valid = True
                            
                            # Critério 2: Tem link de restaurante ou imagem
                            try:
                                has_restaurant_link = element.locator('a[href*="/delivery/"], a[href*="/store/"], a[href*="/restaurant/"]').count() > 0
                                has_image = element.locator('img').count() > 0
                                if has_restaurant_link or (has_image and len(text_content) > 5):
                                    is_valid = True
                            except:
                                pass
                            
                            # Critério 3: Estrutura típica de card de restaurante
                            try:
                                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                                if len(lines) >= 2:
                                    # Primeiro item pode ser nome, segundo pode ser categoria ou avaliação
                                    first_line = lines[0]
                                    if len(first_line) > 3 and not first_line.replace('.', '').replace(',', '').isdigit():
                                        is_valid = True
                            except:
                                pass
                            
                            # Critério 4: Elemento com atributos específicos
                            try:
                                element_html = element.get_attribute('outerHTML') or ""
                                if any(attr in element_html.lower() for attr in [
                                    'restaurant', 'store', 'data-testid', 'delivery'
                                ]):
                                    is_valid = True
                            except:
                                pass
                            
                            if is_valid:
                                valid_elements.append(element)
                                
                        except Exception as e:
                            self.logger.debug(f"Erro ao validar elemento: {e}")
                            continue
                    
                    # Sempre pega o seletor que retorna mais elementos válidos
                    if len(valid_elements) > len(restaurant_elements):
                        restaurant_elements = valid_elements
                        successful_selector = selector
                        self.logger.info(f"Seletor '{selector}': {len(valid_elements)} restaurantes válidos encontrados")
                    
                except Exception as e:
                    self.logger.debug(f"Seletor '{selector}' falhou: {str(e)}")
                    continue
            
            extraction_stats['total'] = len(restaurant_elements)
            
            if len(restaurant_elements) == 0:
                self.logger.warning("AVISO: Nenhum restaurante encontrado com nenhum seletor!")
                # Como último recurso, tenta capturar qualquer elemento que contenha informações de restaurante
                try:
                    fallback_elements = self.page.locator('*').filter(has_text='R$').all()
                    restaurant_elements = fallback_elements[:20]  # Limita a 20 para não sobrecarregar
                    extraction_stats['total'] = len(restaurant_elements)
                    self.logger.info(f"Fallback: {len(restaurant_elements)} elementos com 'R$' encontrados")
                except:
                    pass
            else:
                self.logger.info(f"SUCESSO: {len(restaurant_elements)} restaurantes encontrados usando '{successful_selector}'")
            
            # Extrai dados de cada restaurante
            for i, element in enumerate(restaurant_elements, 1):
                try:
                    restaurant_data = self._extract_restaurant_data(element, i, extraction_stats['total'])
                    
                    if restaurant_data:
                        restaurant = Restaurant(**restaurant_data)
                        self.restaurants.append(restaurant)
                        extraction_stats['success'] += 1
                        self.logger.info(f"SUCESSO [{i}/{extraction_stats['total']}] {restaurant_data['nome']}")
                    else:
                        self.logger.debug(f"AVISO [{i}/{extraction_stats['total']}] Restaurante ignorado (dados incompletos)")
                    
                    # Delay entre extrações
                    self.human.random_delay(0.2, 0.5)
                    
                except Exception as e:
                    extraction_stats['errors'] += 1
                    self.logger.warning(f"ERRO [{i}/{extraction_stats['total']}] Erro ao extrair restaurante: {str(e)[:100]}")
                    continue
            
            # Resumo da extração
            self.logger.info(f"\nResumo da extração:")
            self.logger.info(f"  Total encontrado: {extraction_stats['total']}")
            self.logger.info(f"  Sucesso: {extraction_stats['success']}")
            self.logger.info(f"  Erros: {extraction_stats['errors']}")
            
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
    
    def _scroll_to_load_restaurants(self):
        """Faz scroll para carregar mais restaurantes (lazy loading) - versão otimizada"""
        try:
            self.logger.info("Iniciando scroll progressivo para carregar TODOS os restaurantes...")
            
            # Configurações mais agressivas para capturar mais restaurantes
            last_height = self.page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 25  # Aumentado para capturar mais
            stagnant_attempts = 0
            max_stagnant = 3  # Máximo de tentativas sem mudança
            
            # Conta inicial de restaurantes
            initial_count = self._count_restaurants_on_page()
            self.logger.info(f"Restaurantes iniciais visíveis: {initial_count}")
            
            while scroll_attempts < max_scrolls and stagnant_attempts < max_stagnant:
                # Scroll em etapas menores para trigger lazy loading
                viewport_height = self.page.evaluate("window.innerHeight")
                scroll_step = viewport_height * 0.75  # 75% da altura da viewport
                
                # Faz múltiplos scrolls pequenos
                for i in range(3):
                    self.page.evaluate(f"window.scrollBy(0, {scroll_step})")
                    self.human.random_delay(0.8, 1.2)
                
                # Pausa maior para permitir carregamento
                self.human.random_delay(2, 3)
                
                # Verifica se há mais conteúdo
                new_height = self.page.evaluate("document.body.scrollHeight")
                current_count = self._count_restaurants_on_page()
                
                if new_height == last_height:
                    stagnant_attempts += 1
                    self.logger.info(f"Altura não mudou (tentativa {stagnant_attempts}/{max_stagnant})")
                    
                    # Estratégia mais agressiva quando não há mudança
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    self.human.random_delay(3, 5)
                    
                    # Tenta trigger manual de lazy loading
                    self.page.evaluate("""
                        // Trigger eventos que podem ativar lazy loading
                        window.dispatchEvent(new Event('scroll'));
                        window.dispatchEvent(new Event('resize'));
                        
                        // Força reflow
                        document.body.offsetHeight;
                    """)
                    self.human.random_delay(2, 3)
                    
                    # Verifica novamente
                    newer_height = self.page.evaluate("document.body.scrollHeight")
                    newer_count = self._count_restaurants_on_page()
                    
                    if newer_height == new_height and newer_count == current_count:
                        self.logger.info(f"Nenhuma mudança detectada após estratégia agressiva")
                    else:
                        new_height = newer_height
                        current_count = newer_count
                        stagnant_attempts = 0  # Reset contador
                else:
                    stagnant_attempts = 0  # Reset contador quando há progresso
                
                last_height = new_height
                scroll_attempts += 1
                
                self.logger.info(f"Scroll {scroll_attempts}/{max_scrolls} - Altura: {new_height}px - Restaurantes: {current_count}")
                
                # Estratégias extras a partir do 10º scroll
                if scroll_attempts > 10:
                    # Verifica se há botões "Ver mais" ou similares
                    try:
                        load_more_selectors = [
                            'button:has-text("Ver mais")',
                            'button:has-text("Carregar mais")', 
                            'button:has-text("Mostrar mais")',
                            'button:has-text("Mais restaurantes")',
                            'button:has-text("Carregando...")',
                            '[data-testid="load-more"]',
                            '[data-testid="show-more"]',
                            '.load-more-button',
                            '.show-more',
                            '.pagination-next',
                            'button[class*="load"]',
                            'button[class*="more"]',
                            'a:has-text("Próxima")',
                            'a:has-text(">")',
                            # Seletores específicos do iFood
                            '[data-testid="restaurant-list-pagination"]',
                            '[class*="pagination"]',
                            '[class*="load-more"]'
                        ]
                        
                        button_found = False
                        for selector in load_more_selectors:
                            try:
                                elements = self.page.locator(selector)
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
                                            button_found = True
                                            break
                                if button_found:
                                    break
                            except Exception as e:
                                self.logger.debug(f"Erro ao tentar clicar em {selector}: {e}")
                                continue
                        
                        if button_found:
                            # Aguarda carregamento após click
                            self.human.random_delay(3, 5)
                            stagnant_attempts = 0  # Reset contador
                            
                    except Exception as e:
                        self.logger.debug(f"Erro na busca por botões: {e}")
                
                # Estratégia de scroll infinito - simula chegada próxima ao final
                if scroll_attempts > 5:
                    try:
                        # Simula scroll até quase o final da página
                        self.page.evaluate("""
                            const scrollHeight = document.body.scrollHeight;
                            const viewportHeight = window.innerHeight;
                            const scrollPosition = scrollHeight - viewportHeight - 100;
                            window.scrollTo(0, scrollPosition);
                        """)
                        self.human.random_delay(2, 3)
                    except:
                        pass
            
            # Log final
            final_count = self._count_restaurants_on_page()
            self.logger.info(f"Scroll finalizado: {final_count} restaurantes carregados (iniciais: {initial_count})")
            
            # Volta ao topo para começar extração
            self.page.evaluate("window.scrollTo(0, 0)")
            self.human.random_delay(2, 3)
            self.logger.info("Voltando ao topo para iniciar extração...")
            
        except Exception as e:
            self.logger.warning(f"AVISO: Erro durante scroll: {str(e)}")
    
    def _count_restaurants_on_page(self) -> int:
        """Conta quantos restaurantes estão visíveis na página usando a mesma lógica de validação"""
        try:
            max_count = 0
            
            # Usa a mesma lógica de validação do extractor principal
            for selector in self.restaurant_selectors[:5]:  # Apenas os primeiros 5 para performance
                try:
                    elements = self.page.locator(selector).all()
                    valid_count = 0
                    
                    for element in elements[:100]:  # Limita para performance
                        try:
                            text_content = element.inner_text().strip()
                            
                            # Usa critérios simplificados para contagem rápida
                            is_valid = False
                            
                            # Critério rápido: tem informações de restaurante
                            if (len(text_content) > 10 and 
                                ('R$' in text_content or 'min' in text_content)):
                                is_valid = True
                            
                            # Critério rápido: tem link ou imagem
                            elif element.locator('img').count() > 0 and len(text_content) > 5:
                                is_valid = True
                            
                            if is_valid:
                                valid_count += 1
                                
                        except:
                            continue
                    
                    max_count = max(max_count, valid_count)
                    
                except:
                    continue
            
            # Se não encontrou nada com os seletores principais, usa fallback
            if max_count == 0:
                try:
                    # Fallback: conta elementos que contêm R$ e parecem ter estrutura de restaurante
                    fallback_elements = self.page.locator('*').filter(has_text='R$').all()
                    for element in fallback_elements[:50]:  # Limita para performance
                        try:
                            text = element.inner_text().strip()
                            lines = text.split('\n')
                            if len(lines) >= 2 and len(text) > 15:
                                max_count += 1
                        except:
                            continue
                except:
                    pass
            
            return min(max_count, 500)  # Limite razoável
            
        except:
            return 0
    
    def _extract_restaurant_data(self, element, index: int, total: int) -> Optional[Dict[str, Any]]:
        """Extrai dados de um elemento de restaurante específico"""
        try:
            restaurant_data = {}
            
            # Pega todo o texto do elemento para análise
            full_text = element.inner_text().strip()
            
            # Parse completo do texto estruturado
            parsed_data = self._parse_restaurant_text(full_text)
            
            if not parsed_data or not parsed_data.get('nome'):
                self.logger.debug(f"[{index}/{total}] Elemento ignorado: dados incompletos")
                return None
            
            # Usa dados parseados estruturados
            restaurant_data['nome'] = parsed_data['nome']
            restaurant_data['avaliacao'] = parsed_data.get('rating', 0.0)
            restaurant_data['categoria'] = parsed_data.get('categoria', self.current_category or "Não informado")
            restaurant_data['distancia'] = parsed_data.get('distancia', "Não informado")
            
            # Extrai URL do restaurante
            url = self._extract_restaurant_url(element)
            restaurant_data['url'] = url
            
            # Tempo de entrega - busca padrões específicos no texto
            tempo_entrega = self._extract_delivery_time(full_text)
            restaurant_data['tempo_entrega'] = tempo_entrega
            
            # Taxa de entrega - busca padrões específicos no texto  
            taxa_entrega = self._extract_delivery_fee(full_text)
            restaurant_data['taxa_entrega'] = taxa_entrega
            
            # Endereço/localização (se disponível)
            endereco = self._extract_text_safe(element, [
                '[data-testid="address"]',
                'span[class*="address"]',
                'div[class*="location"]'
            ])
            restaurant_data['endereco'] = endereco
            
            return restaurant_data
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados do restaurante {index}: {str(e)}")
            return None
    
    def _extract_text_safe(self, element, selectors: List[str]) -> Optional[str]:
        """Tenta extrair texto usando múltiplos seletores"""
        for selector in selectors:
            try:
                sub_element = element.locator(selector).first
                if sub_element.count() > 0:
                    text = sub_element.inner_text().strip()
                    if text:
                        return text
            except:
                continue
        return None
    
    def _parse_restaurant_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Faz parse estruturado do texto do restaurante"""
        try:
            if not text:
                return None
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return None
            
            parsed = {}
            
            # Padrão esperado: NOME, RATING, •, CATEGORIA, •, DISTÂNCIA
            # Mas pode variar, então vamos ser flexível
            
            # Primeira linha sempre é o nome
            parsed['nome'] = lines[0]
            
            # Procura rating (número decimal entre 0-5)
            rating = 0.0
            for line in lines[1:]:
                try:
                    if line != '•' and '.' in line and len(line) <= 4:
                        rating_candidate = float(line.replace(',', '.'))
                        if 0 <= rating_candidate <= 5:
                            parsed['rating'] = rating_candidate
                            break
                except:
                    continue
            
            # Procura categoria (linha após rating, ignorando •)
            categoria = None
            for i, line in enumerate(lines):
                if line != '•' and not any(char in line for char in ['.', 'km', 'min', 'R$']):
                    # Se não é o nome e não contém números/símbolos, pode ser categoria
                    if line != parsed['nome']:
                        categoria = line
                        break
            parsed['categoria'] = categoria
            
            # Procura distância (contém 'km')
            distancia = None
            for line in lines:
                if 'km' in line.lower():
                    distancia = line
                    break
            parsed['distancia'] = distancia
            
            return parsed
            
        except Exception as e:
            return None
    
    def _extract_delivery_time(self, text: str) -> str:
        """Extrai tempo de entrega do texto"""
        try:
            import re
            # Busca padrões como "30-40 min", "45 min", "1h 20min"
            time_patterns = [
                r'(\d+-\d+\s*min)',
                r'(\d+\s*min)',
                r'(\d+h\s*\d*min?)',
            ]
            for pattern in time_patterns:
                time_match = re.search(pattern, text, re.IGNORECASE)
                if time_match:
                    return time_match.group(1)
            return "Não informado"
        except:
            return "Não informado"
    
    def _extract_delivery_fee(self, text: str) -> str:
        """Extrai taxa de entrega do texto"""
        try:
            import re
            # Busca padrões de preço ou "grátis"
            fee_patterns = [
                r'(Grátis|grátis|GRÁTIS)',
                r'(R\$\s*\d+[.,]\d+)',
                r'(R\$\s*\d+)',
            ]
            for pattern in fee_patterns:
                fee_match = re.search(pattern, text)
                if fee_match:
                    return fee_match.group(1)
            return "Não informado"
        except:
            return "Não informado"
    
    def _extract_restaurant_url(self, element) -> Optional[str]:
        """Extrai URL do restaurante do elemento"""
        try:
            # Tenta encontrar links diretos no elemento ou seus filhos
            url_selectors = [
                'a[href*="/delivery/"]',  # Links que contêm delivery
                'a[href*="/restaurant/"]',  # Links que contêm restaurant
                'a[href*="/store/"]',  # Links que contêm store
                'a[href]',  # Qualquer link
                '[data-href]',  # Elementos com data-href
                '[onclick*="href"]'  # Elementos com onclick que contém href
            ]
            
            for selector in url_selectors:
                try:
                    link_element = element.locator(selector).first
                    if link_element.count() > 0:
                        href = link_element.get_attribute('href')
                        if href:
                            # Se é uma URL relativa, adiciona o domínio base
                            if href.startswith('/'):
                                href = f"https://www.ifood.com.br{href}"
                            return href
                except:
                    continue
            
            # Tenta buscar por data-href ou outros atributos
            try:
                data_href = element.get_attribute('data-href')
                if data_href:
                    if data_href.startswith('/'):
                        return f"https://www.ifood.com.br{data_href}"
                    return data_href
            except:
                pass
            
            # Como último recurso, tenta encontrar o href no próprio elemento
            try:
                href = element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        return f"https://www.ifood.com.br{href}"
                    return href
            except:
                pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair URL do restaurante: {str(e)}")
            return None
    
    def save_restaurants(self):
        """Salva os restaurantes no banco de dados"""
        ensure_directories()
        
        if not self.restaurants:
            self.logger.warning("AVISO: Nenhum restaurante para salvar")
            return {'new': 0, 'duplicates': 0, 'total': 0}
        
        # Converte restaurantes para formato dict
        restaurants_data = [rest.to_dict() for rest in self.restaurants]
        
        # Salva no banco de dados
        result = self.db.save_restaurants(restaurants_data, self.current_category or "indefinido", self.city)
        
        self.logger.info(f"Resumo do salvamento:")
        self.logger.info(f"  Novos restaurantes: {result['new']}")
        self.logger.info(f"  Duplicados (ignorados): {result['duplicates']}")
        self.logger.info(f"  Total no arquivo: {result['total']}")
        self.logger.info(f"  Arquivo criado: {result.get('file', 'N/A')}")
        
        return result
    
    def run_for_category(self, playwright: Playwright, category_url: str, category_name: str):
        """Executa o scraping para uma categoria específica"""
        ensure_directories()
        
        try:
            self.setup_browser(playwright)
            self.navigate_to_category(category_url, category_name)
            self.extract_restaurants()
            save_result = self.save_restaurants()
            
            return {
                'success': True,
                'category': category_name,
                'restaurants_found': len(self.restaurants),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'total_in_db': save_result['total'],
                'restaurants': self.restaurants
            }
            
        except Exception as e:
            self.logger.error(f"ERRO durante execução para {category_name}: {e}")
            return {
                'success': False,
                'category': category_name,
                'error': str(e),
                'restaurants_found': 0
            }
            
        finally:
            # Remove pausa automática - apenas fecha o navegador
            self.cleanup()