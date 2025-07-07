import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import Playwright, TimeoutError
from src.scrapers.ifood_scraper import IfoodScraper
from src.models.product import Product
from src.utils.helpers import ensure_directories
from src.database.database_adapter import get_database_manager
from src.utils.error_handler import (
    safe_click, safe_fill, validate_page_loaded, 
    with_retry, NavigationError, ElementNotFoundError, DataExtractionError
)
from src.config.settings import SETTINGS


class ProductScraper(IfoodScraper):
    """Scraper específico para extrair produtos/cardápio dos restaurantes"""
    
    def __init__(self, city: str = None, headless: bool = True):
        super().__init__(city, headless)
        self.products: List[Product] = []
        
        # XPath base fornecido (mais específico)
        self.products_list_xpath = '//*[@id="__next"]/div[1]/main/div[1]/div/div[2]/div/div[5]/ul'
        self.product_item_xpath = f'{self.products_list_xpath}/li'
        
        # Seletores mais específicos e abrangentes para produtos
        self.product_selectors = [
            # Seletores baseados no XPath original
            'ul li',  # Items de lista simples
            '#__next li',  # Items dentro do container principal
            'main li',  # Items dentro do main
            
            # Seletores específicos do iFood
            'li[data-testid="dish-card"]',
            'div[data-testid="menu-item"]',
            'article[data-testid="product"]',
            'div[data-testid="dish"]',
            
            # Seletores por classe
            'div[class*="dish-card"]',
            'div[class*="menu-item"]',
            'div[class*="product-card"]',
            'li[class*="product"]',
            'div[class*="item-card"]',
            'article[class*="dish"]',
            
            # Seletores genéricos mas filtrados
            'li:has-text("R$")',  # Items que contêm preço
            'div:has-text("R$"):has-text("Adicionar")',  # Divs com preço e botão
            '*[role="listitem"]',  # Elementos com role de item de lista
        ]
        
        # Seletores para containers de produtos
        self.container_selectors = [
            self.products_list_xpath,
            'ul[class*="menu"]',
            'div[class*="menu-container"]',
            'section[class*="products"]',
            'div[class*="dishes"]',
            'ul[role="list"]'
        ]
        
        self.db = get_database_manager()
        self.current_restaurant = None
        self.current_restaurant_id = None
    
    def navigate_to_restaurant(self, restaurant_url: str, restaurant_name: str):
        """Navega para a página do restaurante"""
        self.current_restaurant = restaurant_name
        
        try:
            self.logger.info(f"Navegando para restaurante: {restaurant_name}")
            self.logger.info(f"URL: {restaurant_url}")
            
            # Navega diretamente para a URL do restaurante
            self.page.goto(restaurant_url, wait_until='domcontentloaded', timeout=30000)
            
            # Aguarda carregamento
            self.page.wait_for_load_state('networkidle', timeout=20000)
            self.wait_with_random_actions(2, 4)
            
            # Verifica se chegou na página correta
            if "delivery" not in self.page.url:
                raise NavigationError("Não chegou na página do restaurante")
            
            self.logger.info(f"SUCESSO: Navegação para {restaurant_name} concluída")
            
        except Exception as e:
            self.logger.error(f"ERRO ao navegar para restaurante {restaurant_name}: {str(e)}")
            raise NavigationError(f"Falha ao navegar para restaurante: {str(e)}")
    
    def _wait_for_products_to_load(self):
        """Aguarda o carregamento dos produtos"""
        try:
            self.logger.info("Aguardando carregamento dos produtos...")
            
            # Tenta aguardar pelo container de produtos
            try:
                self.page.wait_for_selector(self.products_list_xpath, timeout=10000, state="visible")
                self.logger.info("Container de produtos encontrado via XPath")
                return True
            except:
                pass
            
            # Tenta seletores alternativos
            for selector in self.product_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        self.logger.info(f"Produtos encontrados via seletor: {selector}")
                        return True
                except:
                    continue
            
            # Verifica se há mensagem de restaurante fechado
            closed_messages = ["fechado", "closed", "não está aceitando pedidos"]
            page_text = self.page.inner_text("body").lower()
            for msg in closed_messages:
                if msg in page_text:
                    self.logger.warning(f"Restaurante fechado: {msg}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Erro ao aguardar produtos: {str(e)}")
            return False
    
    @with_retry(max_attempts=2, delay=3.0)
    def extract_products(self):
        """Extrai dados dos produtos do restaurante atual"""
        self.logger.info(f"Iniciando extração de produtos do restaurante: {self.current_restaurant}")
        extraction_stats = {'total': 0, 'success': 0, 'errors': 0}
        
        try:
            # Aguarda produtos carregarem
            if not self._wait_for_products_to_load():
                self.logger.warning("Nenhum produto encontrado ou restaurante fechado")
                return
            
            # Faz scroll para carregar todos os produtos
            self._scroll_to_load_all_products()
            
            # Busca produtos usando múltiplas estratégias
            product_elements = self._find_product_elements()
            extraction_stats['total'] = len(product_elements)
            
            if len(product_elements) == 0:
                self.logger.warning("Nenhum produto encontrado após busca")
                return
            
            self.logger.info(f"Encontrados {len(product_elements)} produtos para extrair")
            
            # Extrai dados de cada produto
            for i, element in enumerate(product_elements, 1):
                try:
                    product_data = self._extract_product_data(element, i, extraction_stats['total'])
                    
                    if product_data:
                        product = Product(**product_data)
                        self.products.append(product)
                        extraction_stats['success'] += 1
                        self.logger.info(f"SUCESSO [{i}/{extraction_stats['total']}] {product_data['nome'][:50]}...")
                    
                    # Pequeno delay entre extrações
                    self.human.random_delay(0.1, 0.3)
                    
                except Exception as e:
                    extraction_stats['errors'] += 1
                    self.logger.warning(f"ERRO [{i}/{extraction_stats['total']}] Erro ao extrair produto: {str(e)[:100]}")
                    continue
            
            # Resumo da extração
            self.logger.info(f"\nResumo da extração de produtos:")
            self.logger.info(f"  Total encontrado: {extraction_stats['total']}")
            self.logger.info(f"  Sucesso: {extraction_stats['success']}")
            self.logger.info(f"  Erros: {extraction_stats['errors']}")
            
        except Exception as e:
            self.logger.error(f"ERRO durante extração de produtos: {str(e)}")
            raise DataExtractionError(f"Erro ao extrair produtos: {str(e)}")
    
    def _scroll_to_load_all_products(self):
        """Faz scroll agressivo para carregar TODOS os produtos (lazy loading)"""
        try:
            self.logger.info("Iniciando scroll AGRESSIVO para carregar todos os produtos...")
            
            # Conta produtos iniciais com método específico
            initial_count = self._count_visible_products()
            self.logger.info(f"Produtos inicialmente visíveis: {initial_count}")
            
            # Parâmetros de scroll mais agressivos
            scroll_attempts = 0
            max_scrolls = 50  # Muito mais tentativas
            no_change_count = 0
            max_no_change = 5  # Mais tentativas sem mudança
            consecutive_same = 0
            last_count = initial_count
            
            while scroll_attempts < max_scrolls and no_change_count < max_no_change:
                # Conta produtos antes do scroll
                before_count = self._count_visible_products()
                
                # Estratégias de scroll mais agressivas
                self._perform_aggressive_scroll(scroll_attempts)
                
                # Aguarda carregamento com tempo variável
                wait_time = 1.0 if scroll_attempts < 10 else 2.0
                self.human.random_delay(wait_time, wait_time + 1.0)
                
                # Conta produtos após scroll
                after_count = self._count_visible_products()
                
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
                    self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    self.human.random_delay(2, 3)
            
            final_count = self._count_visible_products()
            self.logger.info(f"Scroll AGRESSIVO concluído: {initial_count} → {final_count} produtos (+{final_count - initial_count})")
            
            # Volta ao topo gradualmente para extração
            self.page.evaluate("window.scrollTo(0, 0)")
            self.human.random_delay(3, 4)
            
        except Exception as e:
            self.logger.warning(f"Erro durante scroll agressivo: {str(e)}")
    
    def _perform_aggressive_scroll(self, attempt):
        """Executa scroll mais agressivo para garantir carregamento completo"""
        try:
            scroll_strategy = attempt % 6
            
            if scroll_strategy == 0:
                # Scroll até o final absoluto
                self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            elif scroll_strategy == 1:
                # Scroll por viewport completo
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            elif scroll_strategy == 2:
                # Scroll por viewport duplo
                self.page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            elif scroll_strategy == 3:
                # Scroll por percentual da página
                self.page.evaluate("window.scrollBy(0, document.documentElement.scrollHeight * 0.3)")
            elif scroll_strategy == 4:
                # Scroll gradual lento
                self.page.evaluate("window.scrollBy(0, window.innerHeight * 0.5)")
            else:
                # Scroll até meio da página
                self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight / 2)")
            
            # A cada 10 tentativas, força interação com containers
            if attempt % 10 == 0:
                try:
                    # Tenta clicar em botões "Ver mais" ou similares
                    more_buttons = self.page.locator('button:has-text("Ver mais"), button:has-text("Carregar mais"), button:has-text("Mostrar mais")').all()
                    for button in more_buttons[:3]:  # Máximo 3 botões
                        try:
                            if button.is_visible():
                                button.click()
                                self.human.random_delay(1, 2)
                                self.logger.info("Clicou em botão 'Ver mais'")
                        except:
                            pass
                            
                    # Tenta scroll em containers específicos
                    for container_selector in self.container_selectors:
                        try:
                            container = self.page.locator(container_selector).first
                            if container.count() > 0:
                                container.scroll_into_view_if_needed()
                                break
                        except:
                            continue
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Erro no scroll agressivo estratégia {attempt}: {str(e)}")
    
    def _count_visible_products(self):
        """Conta produtos visíveis usando seletores mais específicos"""
        counts = {}
        
        # Seletores mais específicos para contagem real de produtos
        specific_selectors = [
            self.product_item_xpath,  # XPath original
            'li[data-testid="dish-card"]',
            'div[data-testid="menu-item"]', 
            'article[data-testid="product"]',
            'div[class*="dish-card"]',
            'li:has-text("R$")',  # Elementos com preço
        ]
        
        for selector in specific_selectors:
            try:
                count = self.page.locator(selector).count()
                if count > 0:
                    counts[selector] = count
                    self.logger.debug(f"Contador {selector}: {count} elementos")
            except:
                continue
        
        if counts:
            # Retorna a contagem do seletor que encontrou mais produtos válidos
            best_selector = max(counts, key=counts.get)
            best_count = counts[best_selector]
            self.logger.info(f"Melhor seletor para contagem: {best_selector} ({best_count} produtos)")
            return best_count
        
        return 0
    
    def _perform_smart_scroll(self, attempt):
        """Executa diferentes estratégias de scroll baseado na tentativa"""
        try:
            if attempt % 4 == 0:
                # Scroll até o final da página
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif attempt % 4 == 1:
                # Scroll gradual por viewport
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            elif attempt % 4 == 2:
                # Scroll médio
                self.page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
            else:
                # Scroll por seções (útil para menus categorizados)
                self.page.evaluate("window.scrollBy(0, window.innerHeight * 0.7)")
            
            # A cada 5 tentativas, tenta scroll em elementos específicos
            if attempt % 5 == 0:
                try:
                    # Tenta scroll em containers específicos
                    for container_selector in self.container_selectors:
                        container = self.page.locator(container_selector).first
                        if container.count() > 0:
                            container.scroll_into_view_if_needed()
                            break
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Erro no scroll estratégia {attempt}: {str(e)}")
    
    def _find_product_elements(self):
        """Busca elementos de produtos usando estratégia melhorada"""
        
        # Seletores específicos para produtos do iFood (mais precisos)
        priority_selectors = [
            self.product_item_xpath,  # XPath original
            'li[data-testid="dish-card"]',  # Cards de pratos específicos
            'div[data-testid="menu-item"]',  # Items de menu
            'article[data-testid="product"]',  # Produtos
            'div[class*="dish-card"]',  # Cards de pratos por classe
            'li[class*="product"]',  # Products por classe
            'div[class*="menu-item"]',  # Items de menu por classe
        ]
        
        # Tenta cada seletor e retorna o que encontrar mais elementos válidos
        best_result = []
        best_selector = None
        best_count = 0
        
        for selector in priority_selectors:
            try:
                elements = self.page.locator(selector).all()
                if len(elements) > best_count:
                    # Valida se os elementos parecem ser produtos reais
                    valid_elements = self._validate_product_elements(elements[:50])  # Limita para validação
                    if len(valid_elements) > best_count:
                        best_result = elements  # Mantém todos os elementos, não só os validados
                        best_selector = selector
                        best_count = len(elements)
                        self.logger.info(f"Melhor seletor até agora: {selector} ({len(elements)} elementos, {len(valid_elements)} válidos)")
            except Exception as e:
                self.logger.debug(f"Erro testando seletor {selector}: {str(e)}")
                continue
        
        if best_result:
            self.logger.info(f"SELETOR FINAL: {best_selector} com {len(best_result)} produtos")
            return best_result
        
        # Fallback: busca por elementos com preço
        self.logger.warning("Nenhum seletor específico funcionou, tentando fallback por preço...")
        try:
            elements = self.page.locator('*:has-text("R$")').all()
            valid_elements = self._validate_product_elements(elements[:100])
            
            if valid_elements:
                self.logger.info(f"Encontrados {len(valid_elements)} produtos via busca por preço")
                return valid_elements
                
        except Exception as e:
            self.logger.error(f"Erro no fallback por preço: {str(e)}")
        
        self.logger.error("ERRO: Nenhum produto encontrado com nenhum seletor!")
        return []
    
    def _validate_product_elements(self, elements):
        """Valida se elementos parecem ser produtos reais"""
        valid_elements = []
        
        for elem in elements:
            try:
                text = elem.inner_text().strip()
                
                # Critérios de validação para produtos
                if (len(text) > 5 and  # Tem texto mínimo
                    len(text) < 1000 and  # Não é texto muito longo
                    ('R$' in text or  # Tem preço OU
                     any(word in text.lower() for word in ['açaí', 'combo', 'ml', 'kg', 'g', 'unid'])  # Tem palavras de produto
                    )):
                    valid_elements.append(elem)
                    
            except Exception as e:
                self.logger.debug(f"Erro validando elemento: {str(e)}")
                continue
                
        return valid_elements
    
    def _extract_product_data(self, element, index: int, total: int) -> Optional[Dict[str, Any]]:
        """Extrai dados de um elemento de produto específico"""
        try:
            product_data = {
                'restaurant_id': self.current_restaurant_id,
                'restaurant_name': self.current_restaurant
            }
            
            # Pega todo o texto do elemento
            full_text = element.inner_text().strip()
            
            # Nome do produto (geralmente a primeira linha ou texto mais proeminente)
            lines = full_text.split('\n')
            product_data['nome'] = lines[0] if lines else "Produto sem nome"
            
            # Descrição (geralmente segunda linha ou texto mais longo)
            if len(lines) > 1:
                # Busca linha que parece ser descrição (não é preço nem tag)
                for line in lines[1:]:
                    if len(line) > 20 and 'R$' not in line and not line.isupper():
                        product_data['descricao'] = line
                        break
            
            # Preço
            price = self._extract_price(full_text)
            product_data['preco'] = price['current']
            product_data['preco_original'] = price['original']
            
            # Categoria do produto (se disponível no elemento)
            product_data['categoria_produto'] = self._extract_product_category(element)
            
            # Imagem
            product_data['imagem_url'] = self._extract_image_url(element)
            
            # Tags/badges (promoção, novo, etc)
            product_data['tags'] = self._extract_tags(full_text)
            
            # Disponibilidade
            product_data['disponivel'] = self._check_availability(element, full_text)
            
            # Informações adicionais
            additional_info = self._extract_additional_info(full_text)
            product_data.update(additional_info)
            
            return product_data
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados do produto {index}: {str(e)}")
            return None
    
    def _extract_price(self, text: str) -> Dict[str, Optional[str]]:
        """Extrai preço do texto"""
        try:
            import re
            
            # Padrões de preço
            price_pattern = r'R\$\s*(\d+[.,]\d{2})'
            prices = re.findall(price_pattern, text)
            
            if not prices:
                return {'current': 'Não informado', 'original': None}
            
            if len(prices) == 1:
                return {'current': f'R$ {prices[0]}', 'original': None}
            
            # Se há 2 preços, pode ser original e com desconto
            if len(prices) >= 2:
                # Assume que o maior é o original e o menor é o atual
                price_values = [float(p.replace(',', '.')) for p in prices]
                if price_values[0] > price_values[1]:
                    return {'current': f'R$ {prices[1]}', 'original': f'R$ {prices[0]}'}
                else:
                    return {'current': f'R$ {prices[0]}', 'original': f'R$ {prices[1]}'}
            
            return {'current': f'R$ {prices[0]}', 'original': None}
            
        except:
            return {'current': 'Não informado', 'original': None}
    
    def _extract_product_category(self, element) -> str:
        """Extrai categoria do produto se disponível"""
        try:
            # Busca por elementos que indiquem categoria
            category_selectors = [
                '[data-testid="category-name"]',
                '[class*="category"]',
                '[class*="section"]'
            ]
            
            for selector in category_selectors:
                try:
                    cat_elem = element.locator(selector).first
                    if cat_elem.count() > 0:
                        return cat_elem.inner_text().strip()
                except:
                    continue
            
            return "Não categorizado"
            
        except:
            return "Não categorizado"
    
    def _extract_image_url(self, element) -> Optional[str]:
        """Extrai URL da imagem do produto"""
        try:
            # Busca imagens no elemento
            img_element = element.locator('img').first
            if img_element.count() > 0:
                src = img_element.get_attribute('src')
                if src and src.startswith('http'):
                    return src
            
            # Tenta background-image
            style_elements = element.locator('[style*="background-image"]').all()
            for style_elem in style_elements:
                style = style_elem.get_attribute('style')
                if style and 'url(' in style:
                    import re
                    url_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    if url_match:
                        return url_match.group(1)
            
            return None
            
        except:
            return None
    
    def _extract_tags(self, text: str) -> Optional[List[str]]:
        """Extrai tags/badges do produto"""
        tags = []
        
        # Palavras que indicam tags
        tag_keywords = [
            'promoção', 'desconto', 'novo', 'mais pedido', 
            'destaque', 'especial', 'limitado', 'vegano',
            'vegetariano', 'sem glúten', 'fit', 'light',
            'picante', 'promocao', '%', 'off'
        ]
        
        text_lower = text.lower()
        for keyword in tag_keywords:
            if keyword in text_lower:
                tags.append(keyword.title())
        
        return tags if tags else None
    
    def _check_availability(self, element, text: str) -> bool:
        """Verifica se o produto está disponível"""
        unavailable_keywords = [
            'indisponível', 'esgotado', 'sold out', 
            'unavailable', 'fora de estoque'
        ]
        
        text_lower = text.lower()
        for keyword in unavailable_keywords:
            if keyword in text_lower:
                return False
        
        # Verifica se o elemento está desabilitado
        try:
            if element.get_attribute('disabled'):
                return False
        except:
            pass
        
        return True
    
    def _extract_additional_info(self, text: str) -> Dict[str, Any]:
        """Extrai informações adicionais do produto"""
        info = {}
        
        # Serve quantas pessoas
        import re
        serves_match = re.search(r'serve[s]?\s*(\d+)\s*pessoa', text, re.IGNORECASE)
        if serves_match:
            info['serve_pessoas'] = int(serves_match.group(1))
        
        # Tempo de preparo
        time_match = re.search(r'(\d+[-\s]?\d*)\s*min', text, re.IGNORECASE)
        if time_match:
            info['tempo_preparo'] = time_match.group(0)
        
        # Calorias
        cal_match = re.search(r'(\d+)\s*kcal|calorias', text, re.IGNORECASE)
        if cal_match:
            info['calorias'] = cal_match.group(0)
        
        return info
    
    def save_products(self):
        """Salva os produtos no banco de dados"""
        ensure_directories()
        
        if not self.products:
            self.logger.warning("Nenhum produto para salvar")
            return {'new': 0, 'duplicates': 0, 'total': 0}
        
        # Converte produtos para formato dict
        products_data = [prod.to_dict() for prod in self.products]
        
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
        
        try:
            self.setup_browser(playwright)
            self.navigate_to_restaurant(restaurant_url, restaurant_name)
            self.extract_products()
            save_result = self.save_products()
            
            return {
                'success': True,
                'restaurant': restaurant_name,
                'products_found': len(self.products),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'products': self.products
            }
            
        except Exception as e:
            self.logger.error(f"ERRO durante execução para {restaurant_name}: {e}")
            return {
                'success': False,
                'restaurant': restaurant_name,
                'error': str(e),
                'products_found': 0
            }
            
        finally:
            self.cleanup()