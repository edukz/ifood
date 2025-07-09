from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv(override=True)


@dataclass
class ScraperSettings:
    """Configurações do web scraper"""
    headless: bool = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
    timeout: int = int(os.getenv('BROWSER_TIMEOUT', 30000))
    wait_time: int = 3
    city: str = os.getenv('DEFAULT_CITY', 'Birigui').strip('"')
    
    # Diretórios
    output_dir: str = os.getenv('OUTPUT_DIR', 'data').strip('"')
    categories_dir: str = "data/categories"
    restaurants_dir: str = "data/restaurants"
    products_dir: str = "data/products"
    log_dir: str = "logs"
    screenshot_dir: str = "archive/screenshots"
    
    # Configurações de Log
    log_retention_days: int = 7    # Dias para manter logs
    log_max_size_mb: int = 50      # Tamanho máximo de log antes de rotacionar
    log_to_console: bool = True    # Mostrar logs no console
    log_to_file: bool = True       # Salvar logs em arquivo
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')        # Nível de log (DEBUG, INFO, WARNING, ERROR)
    

@dataclass
class IfoodSelectors:
    """Seletores XPath e CSS do iFood"""
    address_input: str = '//*[@id="__next"]/section[2]/div/form/div/input'
    confirm_button_1: str = 'xpath=/html/body/div[6]/div/div/div/div/div[3]/button'
    confirm_button_2: str = 'xpath=/html/body/div[6]/div/div/div/div/div[2]/div[2]/form/div[4]/button'
    restaurants_section: str = '//*[@id="__next"]/div[1]/main/div/div[2]/section/article[1]/section[1]/div/div/div[1]/div[1]'
    categories_container: str = '//*[@id="__next"]/div[1]/main/div/div[2]/section/article[1]/section[1]/div/div/div[1]'
    

SETTINGS = ScraperSettings()
SELECTORS = IfoodSelectors()