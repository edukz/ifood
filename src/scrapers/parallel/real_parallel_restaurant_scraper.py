"""
Extrator paralelo REAL de restaurantes
Usa o RestaurantScraper real em paralelo com ThreadPoolExecutor
"""

import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from playwright.sync_api import sync_playwright
from src.scrapers.restaurant_scraper import RestaurantScraper
from src.utils.logger import setup_logger
from src.utils.database import DatabaseManager


class RealParallelRestaurantScraper:
    """Extrator paralelo que usa RestaurantScraper REAL"""
    
    def __init__(self, max_workers: int = 3, headless: bool = True):
        self.max_workers = max_workers
        self.headless = headless
        self.logger = setup_logger(self.__class__.__name__)
        self.db = DatabaseManager()
        self.results_lock = threading.Lock()
        self.all_results = []
        
        # Estatísticas
        self.stats = {
            'total_categories': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'total_restaurants': 0,
            'total_new_saved': 0,
            'total_duplicates': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _extract_category_worker(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Worker que extrai uma categoria usando RestaurantScraper real"""
        category_name = category_data['name']
        category_url = category_data['url']
        worker_id = threading.current_thread().ident
        
        self.logger.info(f"[Worker {worker_id}] Iniciando extração de {category_name}")
        
        try:
            # Cria RestaurantScraper para esta categoria
            scraper = RestaurantScraper(
                city=category_data.get('city', 'Birigui'),
                headless=self.headless
            )
            
            # Executa extração real com Playwright
            with sync_playwright() as playwright:
                result = scraper.run_for_category(
                    playwright=playwright,
                    category_url=category_url,
                    category_name=category_name
                )
            
            # Atualiza estatísticas thread-safe
            with self.results_lock:
                self.all_results.append(result)
                self.stats['processed'] += 1
                
                if result['success']:
                    self.stats['success'] += 1
                    self.stats['total_restaurants'] += result['restaurants_found']
                    self.stats['total_new_saved'] += result['new_saved']
                    self.stats['total_duplicates'] += result['duplicates']
                    
                    self.logger.info(
                        f"[Worker {worker_id}] ✅ {category_name}: "
                        f"{result['restaurants_found']} encontrados, "
                        f"{result['new_saved']} novos salvos"
                    )
                else:
                    self.stats['failed'] += 1
                    self.logger.error(
                        f"[Worker {worker_id}] ❌ {category_name}: "
                        f"{result.get('error', 'Erro desconhecido')}"
                    )
            
            return result
            
        except Exception as e:
            # Atualiza estatísticas de erro
            with self.results_lock:
                self.stats['processed'] += 1
                self.stats['failed'] += 1
            
            error_msg = str(e)
            self.logger.error(f"[Worker {worker_id}] ❌ Erro em {category_name}: {error_msg}")
            
            return {
                'success': False,
                'category': category_name,
                'error': error_msg,
                'restaurants_found': 0,
                'new_saved': 0,
                'duplicates': 0
            }
    
    def extract_parallel(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai restaurantes de múltiplas categorias em paralelo REAL"""
        if not categories:
            return {
                'success': False,
                'error': 'Nenhuma categoria fornecida',
                'stats': self.stats
            }
        
        self.stats['total_categories'] = len(categories)
        self.stats['start_time'] = datetime.now()
        
        self.logger.info(f"🚀 Iniciando extração paralela REAL de {len(categories)} categorias")
        self.logger.info(f"🔧 Usando {self.max_workers} workers simultâneos")
        self.logger.info(f"⚠️  ATENÇÃO: Isso pode demorar 10-30 minutos!")
        
        # Usa ThreadPoolExecutor para paralelismo real
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submete todas as categorias para processamento
            future_to_category = {
                executor.submit(self._extract_category_worker, cat): cat 
                for cat in categories
            }
            
            # Processa resultados conforme completam
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    result = future.result()
                    
                    # Log de progresso
                    progress = (self.stats['processed'] / self.stats['total_categories']) * 100
                    self.logger.info(
                        f"📊 Progresso: {self.stats['processed']}/{self.stats['total_categories']} "
                        f"({progress:.1f}%) - {category['name']} concluída"
                    )
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro inesperado processando {category['name']}: {e}")
        
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Log de resumo final
        self.logger.info("\n" + "="*80)
        self.logger.info("🎉 EXTRAÇÃO PARALELA REAL CONCLUÍDA!")
        self.logger.info("="*80)
        self.logger.info(f"📊 Categorias processadas: {self.stats['processed']}")
        self.logger.info(f"✅ Sucessos: {self.stats['success']}")
        self.logger.info(f"❌ Falhas: {self.stats['failed']}")
        self.logger.info(f"🏪 Total de restaurantes encontrados: {self.stats['total_restaurants']}")
        self.logger.info(f"💾 Total de restaurantes novos salvos: {self.stats['total_new_saved']}")
        self.logger.info(f"🔄 Total de duplicados: {self.stats['total_duplicates']}")
        self.logger.info(f"⏱️  Tempo total: {duration/60:.2f} minutos")
        self.logger.info(f"🚀 Restaurantes por minuto: {self.stats['total_restaurants']/(duration/60):.1f}")
        self.logger.info("="*80)
        
        return {
            'success': True,
            'results': self.all_results,
            'stats': self.stats,
            'duration': duration
        }
    
    def extract_from_database(self) -> Dict[str, Any]:
        """Extrai de todas as categorias no banco usando paralelismo real"""
        try:
            # Busca categorias do banco
            categories = self.db.get_existing_categories()
            
            if not categories:
                return {
                    'success': False,
                    'error': 'Nenhuma categoria encontrada no banco de dados',
                    'stats': self.stats
                }
            
            # Converte para formato esperado
            category_list = []
            for cat in categories:
                if isinstance(cat, dict):
                    category_list.append({
                        'name': cat.get('name', 'Unknown'),
                        'url': cat.get('url', ''),
                        'city': cat.get('city', 'Birigui')
                    })
                elif isinstance(cat, tuple) and len(cat) >= 2:
                    category_list.append({
                        'name': cat[0],
                        'url': cat[1],
                        'city': cat[2] if len(cat) > 2 else 'Birigui'
                    })
            
            # Filtra apenas categorias com URLs válidas
            valid_categories = [cat for cat in category_list if cat['url']]
            
            if not valid_categories:
                return {
                    'success': False,
                    'error': 'Nenhuma categoria com URL válida encontrada',
                    'stats': self.stats
                }
            
            self.logger.info(f"📋 Encontradas {len(valid_categories)} categorias com URLs válidas")
            
            # Executa extração paralela real
            return self.extract_parallel(valid_categories)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair do banco: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def extract_specific_categories(self, category_names: List[str]) -> Dict[str, Any]:
        """Extrai categorias específicas usando paralelismo real"""
        try:
            # Busca todas as categorias
            all_categories = self.db.get_existing_categories()
            
            # Filtra apenas as solicitadas
            category_list = []
            for cat in all_categories:
                cat_name = None
                cat_url = None
                cat_city = 'Birigui'
                
                if isinstance(cat, dict):
                    cat_name = cat.get('name', '')
                    cat_url = cat.get('url', '')
                    cat_city = cat.get('city', 'Birigui')
                elif isinstance(cat, tuple) and len(cat) >= 2:
                    cat_name = cat[0]
                    cat_url = cat[1]
                    cat_city = cat[2] if len(cat) > 2 else 'Birigui'
                
                # Verifica se esta categoria foi solicitada
                if cat_name and any(req_name.lower() in cat_name.lower() for req_name in category_names):
                    category_list.append({
                        'name': cat_name,
                        'url': cat_url,
                        'city': cat_city
                    })
            
            if not category_list:
                return {
                    'success': False,
                    'error': f'Nenhuma categoria encontrada para: {", ".join(category_names)}',
                    'stats': self.stats
                }
            
            self.logger.info(f"🎯 Extraindo {len(category_list)} categorias específicas")
            
            # Executa extração paralela real
            return self.extract_parallel(category_list)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair categorias específicas: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }


# Funções auxiliares
def extract_all_restaurants_parallel_real(max_workers: int = 3, headless: bool = True) -> Dict[str, Any]:
    """Extrai todas as categorias usando paralelismo REAL"""
    scraper = RealParallelRestaurantScraper(max_workers=max_workers, headless=headless)
    return scraper.extract_from_database()


def extract_specific_restaurants_parallel_real(category_names: List[str], 
                                              max_workers: int = 3, 
                                              headless: bool = True) -> Dict[str, Any]:
    """Extrai categorias específicas usando paralelismo REAL"""
    scraper = RealParallelRestaurantScraper(max_workers=max_workers, headless=headless)
    return scraper.extract_specific_categories(category_names)


if __name__ == "__main__":
    # Teste
    print("🧪 Testando extração paralela REAL...")
    
    # Teste com categorias específicas
    result = extract_specific_restaurants_parallel_real(
        category_names=['Pizza', 'Lanches'], 
        max_workers=2
    )
    
    if result['success']:
        print(f"✅ Sucesso!")
        print(f"📊 Estatísticas: {result['stats']}")
    else:
        print(f"❌ Erro: {result['error']}")