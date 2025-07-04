from abc import ABC, abstractmethod
from playwright.sync_api import Page, Browser, BrowserContext
from src.utils.logger import setup_logger
from src.config.browser_config import BrowserConfig
from src.utils.human_behavior import HumanBehavior
from src.utils.error_handler import ErrorHandler, ScraperError
import time
import random


class BaseScraper(ABC):
    """Classe base para scrapers"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.logger = setup_logger(self.__class__.__name__)
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.human = HumanBehavior()
        self.error_handler = ErrorHandler()
    
    @abstractmethod
    def navigate(self):
        """Navega até a página alvo"""
        pass
    
    @abstractmethod
    def extract_data(self):
        """Extrai dados da página"""
        pass
    
    def setup_browser(self, playwright):
        """Configura o navegador com comportamento mais humano"""
        self.logger.info(f"Iniciando browser (headless={self.headless})")
        
        # Configurações do navegador
        launch_options = BrowserConfig.get_launch_options(self.headless)
        self.browser = playwright.chromium.launch(**launch_options)
        
        # Configurações do contexto
        context_options = BrowserConfig.get_browser_context_options()
        self.context = self.browser.new_context(**context_options)
        
        # Adiciona scripts para remover sinais de automação
        self.context.add_init_script("""
            // Remove webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Remove chrome automation
            window.chrome = {
                runtime: {},
            };
            
            // Remove automation in permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        self.page = self.context.new_page()
        
        # Configura timeouts mais humanos
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        self.logger.info("Browser configurado com sucesso")
    
    def wait_with_random_actions(self, min_wait: float = 1, max_wait: float = 3):
        """Espera com ações aleatórias para parecer mais humano"""
        total_wait = self.human.random_delay(min_wait, max_wait)
        start_time = time.time()
        
        while time.time() - start_time < total_wait:
            action = random.choice([
                lambda: self.human.random_mouse_movement(self.page, steps=2),
                lambda: time.sleep(0.5),
                lambda: time.sleep(0.8),
            ])
            action()
    
    def cleanup(self):
        """Fecha o navegador e libera recursos"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        self.logger.info("Browser fechado")