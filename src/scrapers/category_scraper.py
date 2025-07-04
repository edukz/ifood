import json
import time
from typing import List, Dict, Any
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
from src.models.category import Category
from src.utils.helpers import ensure_directories
from src.utils.database import DatabaseManager
from src.utils.error_handler import DataExtractionError, with_retry
from src.config.settings import SETTINGS


class CategoryScraper(IfoodScraper):
    """Scraper específico para extrair categorias do iFood"""
    
    def __init__(self, city: str = None, headless: bool = False):
        super().__init__(city, headless)
        self.categories: List[Category] = []
        self.categories_container_xpath = '//*[@id="__next"]/div[1]/main/div/div[2]/section/article[1]/section[1]/div/div/div[1]'
        self.db = DatabaseManager()
    
    @with_retry(max_attempts=2, delay=3.0)
    def extract_categories(self):
        """Extrai todas as categorias de comida disponíveis"""
        self.logger.info("Iniciando extração de categorias...")
        extraction_stats = {'total': 0, 'success': 0, 'errors': 0}
        
        try:
            # Aguarda container de categorias carregar
            self.logger.info("Aguardando container de categorias...")
            try:
                self.page.wait_for_selector(self.categories_container_xpath, timeout=15000, state="visible")
            except TimeoutError:
                self.error_handler.take_screenshot(self.page, "categories_container_timeout")
                self.error_handler.log_page_state(self.page)
                raise DataExtractionError("Container de categorias não encontrado")
            
            self.human.random_wait()
            
            # Encontra o container principal
            container = self.page.locator(self.categories_container_xpath)
            
            # Verifica se o container existe e está visível
            if not container.is_visible():
                self.error_handler.take_screenshot(self.page, "categories_container_not_visible")
                raise DataExtractionError("Container de categorias não está visível")
            
            # Pequena pausa para garantir carregamento completo
            self.human.random_wait()
            
            # Busca todas as divs filhas que contêm links
            category_elements = container.locator('div > a').all()
            extraction_stats['total'] = len(category_elements)
            
            self.logger.info(f"Encontradas {len(category_elements)} possíveis categorias")
            
            if len(category_elements) == 0:
                self.logger.warning("AVISO: Nenhuma categoria encontrada, tentando seletores alternativos...")
                # Tenta seletores alternativos
                alternative_selectors = [
                    f"{self.categories_container_xpath} a",
                    f"{self.categories_container_xpath} [href*='/delivery/']",
                    "a[href*='/delivery/'][href*='/restaurantes']"
                ]
                
                for alt_selector in alternative_selectors:
                    try:
                        alt_elements = self.page.locator(alt_selector).all()
                        if len(alt_elements) > 0:
                            category_elements = alt_elements
                            extraction_stats['total'] = len(category_elements)
                            self.logger.info(f"SUCESSO: Encontradas {len(alt_elements)} categorias com seletor alternativo")
                            break
                    except:
                        continue
            
            for i, element in enumerate(category_elements, 1):
                try:
                    # Extrai informações da categoria
                    href = element.get_attribute('href')
                    
                    if not href:
                        continue
                    
                    # Constrói URL completa se necessário
                    if href.startswith('/'):
                        full_url = f"https://www.ifood.com.br{href}"
                    else:
                        full_url = href
                    
                    # Tenta extrair o nome da categoria
                    name = None
                    
                    # Primeiro tenta pegar texto direto
                    try:
                        name = element.inner_text().strip()
                    except:
                        pass
                    
                    # Se não conseguiu, tenta pegar de elementos internos
                    if not name:
                        try:
                            name_element = element.locator('span').first
                            if name_element.count() > 0:
                                name = name_element.inner_text().strip()
                        except:
                            pass
                    
                    # Tenta extrair URL do ícone/imagem
                    icon_url = None
                    try:
                        img = element.locator('img').first
                        if img.count() > 0:
                            icon_url = img.get_attribute('src')
                    except:
                        pass
                    
                    # Se conseguiu extrair nome e URL, adiciona à lista
                    if name and href:
                        category = Category(
                            name=name,
                            url=full_url,
                            icon_url=icon_url
                        )
                        self.categories.append(category)
                        extraction_stats['success'] += 1
                        self.logger.info(f"SUCESSO [{i}/{extraction_stats['total']}] {name} -> {category.slug}")
                    else:
                        self.logger.debug(f"AVISO [{i}/{extraction_stats['total']}] Categoria ignorada (dados incompletos)")
                    
                    # Pequeno delay entre extrações
                    self.human.random_delay(0.1, 0.3)
                    
                except Exception as e:
                    extraction_stats['errors'] += 1
                    self.logger.warning(f"ERRO [{i}/{extraction_stats['total']}] Erro ao extrair categoria: {str(e)[:100]}")
                    continue
            
            # Resumo da extração
            self.logger.info(f"\nResumo da extração:")
            self.logger.info(f"  Total encontrado: {extraction_stats['total']}")
            self.logger.info(f"  Sucesso: {extraction_stats['success']}")
            self.logger.info(f"  Erros: {extraction_stats['errors']}")
            
            if len(self.categories) == 0:
                self.error_handler.take_screenshot(self.page, "no_categories_extracted")
                raise DataExtractionError("Nenhuma categoria foi extraída com sucesso")
            
        except (TimeoutError, DataExtractionError) as e:
            self.logger.error(f"ERRO durante extração: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"ERRO inesperado: {str(e)}")
            self.error_handler.take_screenshot(self.page, "unexpected_extraction_error")
            raise DataExtractionError(f"Erro ao extrair categorias: {str(e)}")
    
    def save_categories(self):
        """Salva as categorias no banco de dados"""
        ensure_directories()
        
        # Converte categorias para formato dict
        categories_data = [cat.to_dict() for cat in self.categories]
        
        # Salva no banco de dados
        result = self.db.save_categories(categories_data, self.city)
        
        self.logger.info(f"Resumo do salvamento:")
        self.logger.info(f"  Novas categorias: {result['new']}")
        self.logger.info(f"  Duplicadas (ignoradas): {result['duplicates']}")
        self.logger.info(f"  Total no banco: {result['total']}")
        
        return result
    
    def run(self, playwright: Playwright):
        """Executa o processo completo de extração de categorias"""
        ensure_directories()
        
        try:
            # Verifica categorias existentes antes de iniciar
            existing = self.db.get_existing_categories(self.city)
            if existing:
                self.logger.info(f"INFO: Já existem {len(existing)} categorias para {self.city} no banco")
            
            self.setup_browser(playwright)
            self.navigate()  # Navega até a página de restaurantes
            self.extract_categories()  # Extrai as categorias
            save_result = self.save_categories()  # Salva no banco
            
            return {
                'success': True,
                'categories_found': len(self.categories),
                'new_saved': save_result['new'],
                'duplicates': save_result['duplicates'],
                'total_in_db': save_result['total'],
                'categories': self.categories
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante execução: {e}")
            return {
                'success': False,
                'error': str(e),
                'categories_found': 0
            }
            
        finally:
            if not self.headless:
                input("Pressione Enter para fechar o navegador...")
            self.cleanup()