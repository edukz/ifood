import time
from typing import List, Dict, Any
from playwright.sync_api import Playwright, TimeoutError
from src.scrapers.base import BaseScraper
from src.config.settings import SETTINGS, SELECTORS
from src.utils.helpers import ensure_directories
from src.utils.human_behavior import HumanBehavior
from src.utils.error_handler import (
    safe_click, safe_fill, validate_page_loaded, 
    with_retry, NavigationError, ElementNotFoundError
)


class IfoodScraper(BaseScraper):
    """Scraper específico para o iFood"""
    
    def __init__(self, city: str = None, headless: bool = False):
        super().__init__(headless)
        self.city = city or SETTINGS.city
        self.base_url = "https://www.ifood.com.br"
        self.restaurants_data: List[Dict[str, Any]] = []
    
    @with_retry(max_attempts=3, delay=2.0)
    def navigate(self):
        """Navega até a seção de restaurantes com comportamento humano e tratamento de erros"""
        step = "inicial"
        
        try:
            # PASSO 1: Acessar o site
            step = "acessar_site"
            self.logger.info(f"Passo 1/4: Acessando {self.base_url}")
            self.page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
            
            # Valida se a página carregou corretamente
            if not validate_page_loaded(self.page, "ifood.com.br"):
                raise NavigationError("Página do iFood não carregou corretamente")
            
            # Movimento inicial do mouse
            self.human.random_mouse_movement(self.page, steps=2)
            self.page.wait_for_load_state('networkidle', timeout=15000)
            self.wait_with_random_actions(1, 2)
            
            # PASSO 2: Preencher cidade
            step = "preencher_cidade"
            self.logger.info(f"Passo 2/4: Preenchendo cidade: {self.city}")
            
            # Aguarda campo de endereço estar disponível
            try:
                self.page.wait_for_selector(SELECTORS.address_input, state="visible", timeout=10000)
            except TimeoutError:
                self.error_handler.take_screenshot(self.page, "address_input_not_found")
                self.error_handler.log_page_state(self.page)
                raise ElementNotFoundError("Campo de endereço não encontrado")
            
            # Usa safe_click e safe_fill
            safe_click(self.page, SELECTORS.address_input)
            time.sleep(0.5)
            safe_fill(self.page, SELECTORS.address_input, self.city)
            
            # Aguardar dropdown e movimentos aleatórios
            self.logger.info("Aguardando opções de endereço...")
            self.wait_with_random_actions(2, 4)
            
            # Simula leitura antes de selecionar
            self.human.simulate_reading_time(len(self.city) * 10)
            self.page.keyboard.press("Enter")
            
            # PASSO 3: Confirmar localização (primeira vez)
            step = "confirmar_localizacao_1"
            self.logger.info("Passo 3/4: Confirmando localização (1/2)...")
            self.human.random_wait()
            
            try:
                # Tenta com o seletor original
                self.human.random_mouse_hover(self.page, SELECTORS.confirm_button_1)
                safe_click(self.page, SELECTORS.confirm_button_1, timeout=10000)
            except ElementNotFoundError:
                self.logger.warning("AVISO: Botão de confirmação 1 não encontrado, tentando alternativas...")
                # Tenta seletores alternativos
                alternative_selectors = [
                    'button:has-text("Confirmar")',
                    'button:has-text("Continuar")',
                    '[data-testid="confirm-button"]',
                    '.confirmation-button'
                ]
                
                found = False
                for alt_selector in alternative_selectors:
                    try:
                        if self.page.locator(alt_selector).count() > 0:
                            safe_click(self.page, alt_selector)
                            found = True
                            self.logger.info(f"SUCESSO: Usado seletor alternativo: {alt_selector}")
                            break
                    except:
                        continue
                
                if not found:
                    self.error_handler.take_screenshot(self.page, "confirm_button_1_not_found")
                    raise
            
            # PASSO 4: Confirmar localização (segunda vez)
            step = "confirmar_localizacao_2"
            self.wait_with_random_actions(1.5, 3)
            self.logger.info("Passo 4/4: Confirmando localização (2/2)...")
            
            try:
                self.human.random_mouse_hover(self.page, SELECTORS.confirm_button_2)
                self.human.random_wait()
                safe_click(self.page, SELECTORS.confirm_button_2, timeout=10000)
            except ElementNotFoundError:
                self.logger.warning("AVISO: Botão de confirmação 2 não encontrado, pode já estar na página correta")
                # Verifica se já está na página de restaurantes
                if "restaurante" in self.page.url or "delivery" in self.page.url:
                    self.logger.info("SUCESSO: Já está na página de restaurantes")
                else:
                    raise
            
            # PASSO 5: Acessar seção de restaurantes
            step = "acessar_restaurantes"
            self.wait_with_random_actions(2, 4)
            self.logger.info("Acessando seção de restaurantes...")
            
            try:
                self.human.random_mouse_hover(self.page, SELECTORS.restaurants_section)
                safe_click(self.page, SELECTORS.restaurants_section, timeout=10000)
            except ElementNotFoundError:
                # Verifica se já está na página correta
                if "restaurante" not in self.page.url and "delivery" not in self.page.url:
                    self.error_handler.take_screenshot(self.page, "restaurants_section_not_found")
                    raise
                else:
                    self.logger.info("SUCESSO: Já está na seção de restaurantes")
            
            # Aguardar carregamento com ações humanas
            self.page.wait_for_load_state('networkidle', timeout=20000)
            self.wait_with_random_actions(3, 5)
            
            # Validação final
            current_url = self.page.url
            if "delivery" in current_url or "restaurante" in current_url:
                self.logger.info("SUCESSO: Navegação concluída com sucesso!")
                self.logger.info(f"URL final: {current_url}")
            else:
                self.logger.warning(f"AVISO: URL suspeita: {current_url}")
                self.error_handler.take_screenshot(self.page, "suspicious_final_url")
            
        except (TimeoutError, ElementNotFoundError, NavigationError) as e:
            self.logger.error(f"ERRO no passo '{step}': {str(e)}")
            self.error_handler.take_screenshot(self.page, f"error_{step}")
            self.error_handler.log_page_state(self.page)
            raise NavigationError(f"Falha na navegação no passo '{step}': {str(e)}")
            
        except Exception as e:
            self.logger.error(f"ERRO inesperado no passo '{step}': {str(e)}")
            self.error_handler.take_screenshot(self.page, f"unexpected_error_{step}")
            self.error_handler.log_page_state(self.page)
            raise
    
    def extract_data(self):
        """Extrai dados dos restaurantes"""
        self.logger.info("Iniciando extração de dados...")
        
        try:
            # TODO: Implementar extração de dados dos restaurantes
            # Por enquanto, apenas retorna dados de exemplo
            self.restaurants_data = [
                {
                    "nome": "Restaurante Exemplo",
                    "categoria": "Pizzaria", 
                    "avaliacao": 4.5,
                    "tempo_entrega": "30-40 min",
                    "taxa_entrega": "R$ 5,00"
                }
            ]
            
            self.logger.info(f"Dados extraídos: {len(self.restaurants_data)} restaurantes")
            
        except Exception as e:
            self.logger.error(f"Erro durante extração: {e}")
            raise
    
    def save_data(self):
        """Salva os dados extraídos no MySQL"""
        if self.restaurants_data:
            from src.utils.database_mysql_monitored import MonitoredDatabaseManager
            
            db_manager = MonitoredDatabaseManager(
                chunk_size=500,
                smart_mode=True,
                enable_monitoring=True
            )
            
            # Salva categorias se houver
            if hasattr(self, 'categories_data') and self.categories_data:
                cat_result = db_manager.save_categories(self.categories_data, "São Paulo")
                self.logger.info(f"Categorias salvas no MySQL: {cat_result}")
            
            # Salva restaurantes
            rest_result = db_manager.save_restaurants(self.restaurants_data, "Geral", "São Paulo")
            self.logger.info(f"Restaurantes salvos no MySQL: {rest_result}")
            
            return f"MySQL: {rest_result.get('new', 0)} novos, {rest_result.get('updated', 0)} atualizados"
        else:
            self.logger.warning("Nenhum dado para salvar")
            return None
    
    def run(self, playwright: Playwright):
        """Executa o processo completo de scraping"""
        ensure_directories()
        
        try:
            self.setup_browser(playwright)
            self.navigate()
            self.extract_data()
            filename = self.save_data()
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro durante execução: {e}")
            raise
            
        finally:
            if not self.headless:
                input("Pressione Enter para fechar o navegador...")
            self.cleanup()