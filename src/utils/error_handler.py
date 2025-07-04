import os
import time
import traceback
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from functools import wraps
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from src.utils.logger import setup_logger


class ScraperError(Exception):
    """Exceção base para erros do scraper"""
    pass


class ElementNotFoundError(ScraperError):
    """Erro quando elemento não é encontrado"""
    pass


class NavigationError(ScraperError):
    """Erro durante navegação"""
    pass


class DataExtractionError(ScraperError):
    """Erro durante extração de dados"""
    pass


class ErrorHandler:
    """Gerenciador centralizado de erros"""
    
    def __init__(self):
        self.logger = setup_logger("ErrorHandler")
        # Screenshots vão direto para archive
        self.screenshots_dir = "archive/screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.error_count = 0
        self.max_retries = 3
        
    def take_screenshot(self, page: Page, error_type: str) -> Optional[str]:
        """Captura screenshot em caso de erro"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.screenshots_dir}/error_{error_type}_{timestamp}.png"
            page.screenshot(path=filename, full_page=True)
            self.logger.info(f"Screenshot salvo: {filename}")
            return filename
        except Exception as e:
            self.logger.warning(f"Não foi possível capturar screenshot: {e}")
            return None
    
    def log_page_state(self, page: Page) -> Dict[str, Any]:
        """Registra estado atual da página para debug"""
        try:
            state = {
                'url': page.url,
                'title': page.title(),
                'viewport': page.viewport_size,
                'timestamp': datetime.now().isoformat()
            }
            
            # Tenta capturar alguns elementos visíveis
            try:
                visible_text = page.locator('body').inner_text()[:500]
                state['visible_text_preview'] = visible_text
            except:
                state['visible_text_preview'] = "Não foi possível capturar texto"
            
            self.logger.debug(f"Estado da página: {state}")
            return state
            
        except Exception as e:
            self.logger.warning(f"Erro ao capturar estado da página: {e}")
            return {}
    
    def handle_element_error(self, page: Page, selector: str, action: str) -> None:
        """Trata erros relacionados a elementos"""
        self.error_count += 1
        
        self.logger.error(f"ERRO: Elemento não encontrado ou não interagível")
        self.logger.error(f"   Seletor: {selector}")
        self.logger.error(f"   Ação tentada: {action}")
        self.logger.error(f"   URL atual: {page.url}")
        
        # Captura screenshot
        self.take_screenshot(page, "element_not_found")
        
        # Registra estado da página
        self.log_page_state(page)
        
        # Verifica se elemento existe mas não está visível
        try:
            elements = page.locator(selector).all()
            if elements:
                self.logger.info(f"INFO: Elemento existe ({len(elements)} encontrados), mas pode não estar visível")
                for i, elem in enumerate(elements[:3]):  # Verifica até 3 elementos
                    try:
                        is_visible = elem.is_visible()
                        is_enabled = elem.is_enabled()
                        self.logger.info(f"   Elemento {i}: visível={is_visible}, habilitado={is_enabled}")
                    except:
                        pass
            else:
                self.logger.info("INFO: Nenhum elemento encontrado com este seletor")
        except:
            pass


def with_retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """Decorator para retry com backoff exponencial"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger = setup_logger("Retry")
                        logger.info(f"RETRY: Tentativa {attempt + 1}/{max_attempts} para {func.__name__}")
                    
                    return func(*args, **kwargs)
                    
                except (PlaywrightTimeoutError, ElementNotFoundError, NavigationError) as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger = setup_logger("Retry")
                        logger.warning(f"AVISO: Erro na tentativa {attempt + 1}: {str(e)}")
                        logger.info(f"AGUARDANDO: {current_delay}s antes de tentar novamente...")
                        
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger = setup_logger("Retry")
                        logger.error(f"ERRO: Todas as {max_attempts} tentativas falharam para {func.__name__}")
                        
            raise last_exception
            
        return wrapper
    return decorator


def safe_click(page: Page, selector: str, timeout: int = 10000) -> bool:
    """Clique seguro com validação e retry"""
    logger = setup_logger("SafeClick")
    error_handler = ErrorHandler()
    
    try:
        # Aguarda elemento aparecer
        logger.debug(f"Aguardando elemento: {selector}")
        page.wait_for_selector(selector, timeout=timeout, state="visible")
        
        # Verifica se está interagível
        element = page.locator(selector).first
        
        if not element.is_visible():
            raise ElementNotFoundError(f"Elemento não está visível: {selector}")
        
        if not element.is_enabled():
            raise ElementNotFoundError(f"Elemento não está habilitado: {selector}")
        
        # Scroll até o elemento se necessário
        element.scroll_into_view_if_needed()
        
        # Pequena pausa antes do clique
        time.sleep(0.5)
        
        # Clica
        element.click()
        logger.debug(f"SUCESSO: Clique realizado em: {selector}")
        return True
        
    except PlaywrightTimeoutError:
        error_handler.handle_element_error(page, selector, "click")
        raise ElementNotFoundError(f"Timeout ao aguardar elemento: {selector}")
        
    except Exception as e:
        error_handler.handle_element_error(page, selector, "click")
        raise ElementNotFoundError(f"Erro ao clicar no elemento: {str(e)}")


def safe_fill(page: Page, selector: str, text: str, timeout: int = 10000) -> bool:
    """Preenchimento seguro com validação"""
    logger = setup_logger("SafeFill")
    error_handler = ErrorHandler()
    
    try:
        # Aguarda elemento
        logger.debug(f"Aguardando campo de input: {selector}")
        page.wait_for_selector(selector, timeout=timeout, state="visible")
        
        element = page.locator(selector).first
        
        if not element.is_visible():
            raise ElementNotFoundError(f"Campo não está visível: {selector}")
        
        if not element.is_enabled():
            raise ElementNotFoundError(f"Campo não está habilitado: {selector}")
        
        # Limpa e preenche
        element.clear()
        element.fill(text)
        
        # Verifica se o texto foi inserido
        actual_value = element.input_value()
        if actual_value != text:
            logger.warning(f"AVISO: Valor inserido diferente do esperado: '{actual_value}' != '{text}'")
        
        logger.debug(f"SUCESSO: Campo preenchido: {selector}")
        return True
        
    except PlaywrightTimeoutError:
        error_handler.handle_element_error(page, selector, "fill")
        raise ElementNotFoundError(f"Timeout ao aguardar campo: {selector}")
        
    except Exception as e:
        error_handler.handle_element_error(page, selector, "fill")
        raise ElementNotFoundError(f"Erro ao preencher campo: {str(e)}")


def validate_page_loaded(page: Page, expected_url_pattern: str = None, expected_title: str = None) -> bool:
    """Valida se a página foi carregada corretamente"""
    logger = setup_logger("PageValidator")
    
    try:
        # Verifica URL se fornecido padrão
        if expected_url_pattern:
            current_url = page.url
            if expected_url_pattern not in current_url:
                logger.error(f"ERRO: URL incorreta: {current_url}")
                logger.error(f"   Esperado padrão: {expected_url_pattern}")
                return False
        
        # Verifica título se fornecido
        if expected_title:
            current_title = page.title()
            if expected_title not in current_title:
                logger.error(f"ERRO: Título incorreto: {current_title}")
                logger.error(f"   Esperado: {expected_title}")
                return False
        
        # Verifica se não há erros evidentes
        error_indicators = [
            "404", "500", "erro", "error", "não encontrad", "not found",
            "página não existe", "page not exist"
        ]
        
        page_text = page.locator('body').inner_text().lower()
        for indicator in error_indicators:
            if indicator in page_text[:500]:  # Verifica apenas início do texto
                logger.error(f"ERRO: Possível página de erro detectada: '{indicator}' encontrado")
                return False
        
        logger.debug("SUCESSO: Página validada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"ERRO: Erro ao validar página: {e}")
        return False