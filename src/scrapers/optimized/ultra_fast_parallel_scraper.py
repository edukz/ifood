"""
Extrator paralelo ULTRA-RÁPIDO
Usa FastRestaurantScraper otimizado
Tempo esperado: 1-2 minutos por categoria vs 5+ minutos original
"""

import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from playwright.sync_api import sync_playwright
from src.scrapers.optimized.fast_restaurant_scraper import FastRestaurantScraper
from src.utils.logger import setup_logger
from src.utils.database import DatabaseManager


class UltraFastParallelScraper:
    """Extrator paralelo ultra-rápido"""
    
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
            'end_time': None,
            'total_duration': 0
        }
    
    def _extract_category_ultra_fast(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Worker ultra-rápido para extração de categoria"""
        category_name = category_data['name']
        category_url = category_data['url']
        worker_id = threading.current_thread().ident
        
        self.logger.info(f"⚡ [Worker {worker_id}] Iniciando {category_name}")
        
        try:
            # Usa o FastRestaurantScraper otimizado
            scraper = FastRestaurantScraper(
                city=category_data.get('city', 'Birigui'),
                headless=self.headless
            )
            
            # Execução ultra-rápida
            with sync_playwright() as playwright:
                result = scraper.run_fast_for_category(
                    playwright=playwright,
                    category_url=category_url,
                    category_name=category_name
                )
            
            # Atualiza estatísticas
            with self.results_lock:
                self.all_results.append(result)
                self.stats['processed'] += 1
                
                if result['success']:
                    self.stats['success'] += 1
                    self.stats['total_restaurants'] += result['restaurants_found']
                    self.stats['total_new_saved'] += result['new_saved']
                    self.stats['total_duplicates'] += result['duplicates']
                    self.stats['total_duration'] += result['duration']
                    
                    self.logger.info(
                        f"⚡ [Worker {worker_id}] ✅ {category_name}: "
                        f"{result['restaurants_found']} encontrados em {result['duration']:.1f}s"
                    )
                else:
                    self.stats['failed'] += 1
                    self.logger.error(
                        f"⚡ [Worker {worker_id}] ❌ {category_name}: "
                        f"{result.get('error', 'Erro')}"
                    )
            
            return result
            
        except Exception as e:
            with self.results_lock:
                self.stats['processed'] += 1
                self.stats['failed'] += 1
            
            error_msg = str(e)
            self.logger.error(f"⚡ [Worker {worker_id}] ❌ {category_name}: {error_msg}")
            
            return {
                'success': False,
                'category': category_name,
                'error': error_msg,
                'restaurants_found': 0,
                'new_saved': 0,
                'duplicates': 0,
                'duration': 0
            }
    
    def extract_ultra_fast(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extração paralela ultra-rápida"""
        if not categories:
            return {
                'success': False,
                'error': 'Nenhuma categoria fornecida',
                'stats': self.stats
            }
        
        self.stats['total_categories'] = len(categories)
        self.stats['start_time'] = datetime.now()
        
        self.logger.info(f"⚡ EXTRAÇÃO ULTRA-RÁPIDA iniciada!")
        self.logger.info(f"📊 {len(categories)} categorias com {self.max_workers} workers")
        self.logger.info(f"🎯 Tempo estimado: {len(categories)*1.5/self.max_workers:.1f} minutos")
        
        # ThreadPoolExecutor otimizado
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="UltraFast") as executor:
            # Submete todas as categorias
            future_to_category = {
                executor.submit(self._extract_category_ultra_fast, cat): cat 
                for cat in categories
            }
            
            # Processa resultados em tempo real
            completed = 0
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                completed += 1
                
                try:
                    result = future.result()
                    
                    # Log de progresso otimizado
                    progress = (completed / len(categories)) * 100
                    eta_seconds = (len(categories) - completed) * (self.stats['total_duration'] / max(completed, 1))
                    
                    self.logger.info(
                        f"⚡ Progresso: {completed}/{len(categories)} ({progress:.0f}%) "
                        f"| ETA: {eta_seconds/60:.1f}min | {category['name']} ✅"
                    )
                    
                except Exception as e:
                    self.logger.error(f"⚡ Erro inesperado {category['name']}: {e}")
        
        self.stats['end_time'] = datetime.now()
        total_duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Relatório final otimizado
        avg_time_per_category = self.stats['total_duration'] / max(self.stats['success'], 1)
        restaurants_per_minute = self.stats['total_restaurants'] / (total_duration / 60)
        
        self.logger.info("\n" + "⚡" * 60)
        self.logger.info("🎉 EXTRAÇÃO ULTRA-RÁPIDA CONCLUÍDA!")
        self.logger.info("⚡" * 60)
        self.logger.info(f"📊 Categorias: {self.stats['processed']} | ✅ {self.stats['success']} | ❌ {self.stats['failed']}")
        self.logger.info(f"🏪 Restaurantes: {self.stats['total_restaurants']} encontrados | {self.stats['total_new_saved']} novos")
        self.logger.info(f"⏱️  Tempo total: {total_duration/60:.1f} min | Média: {avg_time_per_category:.1f}s/categoria")
        self.logger.info(f"🚀 Performance: {restaurants_per_minute:.1f} restaurantes/minuto")
        self.logger.info("⚡" * 60)
        
        return {
            'success': True,
            'results': self.all_results,
            'stats': self.stats,
            'total_duration': total_duration,
            'avg_time_per_category': avg_time_per_category,
            'restaurants_per_minute': restaurants_per_minute
        }
    
    def extract_from_database_ultra_fast(self) -> Dict[str, Any]:
        """Extrai todas as categorias do banco ultra-rápido"""
        try:
            categories = self.db.get_existing_categories()
            
            if not categories:
                return {
                    'success': False,
                    'error': 'Nenhuma categoria no banco',
                    'stats': self.stats
                }
            
            # Converte para formato otimizado
            category_list = []
            for cat in categories:
                if isinstance(cat, dict):
                    if cat.get('url'):  # Apenas categorias com URL
                        category_list.append({
                            'name': cat.get('name', 'Unknown'),
                            'url': cat['url'],
                            'city': cat.get('city', 'Birigui')
                        })
                elif isinstance(cat, tuple) and len(cat) >= 2 and cat[1]:
                    category_list.append({
                        'name': cat[0],
                        'url': cat[1],
                        'city': cat[2] if len(cat) > 2 else 'Birigui'
                    })
            
            if not category_list:
                return {
                    'success': False,
                    'error': 'Nenhuma categoria com URL válida',
                    'stats': self.stats
                }
            
            self.logger.info(f"⚡ {len(category_list)} categorias válidas encontradas")
            
            return self.extract_ultra_fast(category_list)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar categorias: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def extract_specific_ultra_fast(self, category_names: List[str]) -> Dict[str, Any]:
        """Extrai categorias específicas ultra-rápido"""
        try:
            all_categories = self.db.get_existing_categories()
            
            # Filtra categorias solicitadas
            category_list = []
            for cat in all_categories:
                cat_name = cat.get('name', '') if isinstance(cat, dict) else (cat[0] if cat else '')
                cat_url = cat.get('url', '') if isinstance(cat, dict) else (cat[1] if len(cat) > 1 else '')
                
                if cat_name and cat_url and any(req.lower() in cat_name.lower() for req in category_names):
                    category_list.append({
                        'name': cat_name,
                        'url': cat_url,
                        'city': 'Birigui'
                    })
            
            if not category_list:
                return {
                    'success': False,
                    'error': f'Categorias não encontradas: {", ".join(category_names)}',
                    'stats': self.stats
                }
            
            self.logger.info(f"⚡ {len(category_list)} categorias específicas selecionadas")
            
            return self.extract_ultra_fast(category_list)
            
        except Exception as e:
            self.logger.error(f"❌ Erro na seleção específica: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }


# Funções auxiliares ultra-rápidas
def extract_all_ultra_fast(max_workers: int = 3, headless: bool = True) -> Dict[str, Any]:
    """Extrai todas as categorias ultra-rápido"""
    scraper = UltraFastParallelScraper(max_workers=max_workers, headless=headless)
    return scraper.extract_from_database_ultra_fast()


def extract_specific_ultra_fast(category_names: List[str], 
                               max_workers: int = 3, 
                               headless: bool = True) -> Dict[str, Any]:
    """Extrai categorias específicas ultra-rápido"""
    scraper = UltraFastParallelScraper(max_workers=max_workers, headless=headless)
    return scraper.extract_specific_ultra_fast(category_names)


if __name__ == "__main__":
    # Teste ultra-rápido
    print("⚡ Teste ULTRA-RÁPIDO")
    
    start = time.time()
    result = extract_specific_ultra_fast(['Pizza', 'Lanches'], max_workers=2)
    duration = time.time() - start
    
    if result['success']:
        print(f"✅ Concluído em {duration:.1f}s")
        print(f"📊 {result['stats']['total_restaurants']} restaurantes")
    else:
        print(f"❌ Erro: {result['error']}")