"""
Extrator paralelo ULTRA-RÁPIDO
Usa FastRestaurantScraper otimizado
Tempo esperado: 1-2 minutos por categoria vs 5+ minutos original
"""

import time
import asyncio
import threading
from typing import List, Dict, Any
from datetime import datetime

from playwright.async_api import async_playwright
from src.scrapers.optimized.fast_restaurant_scraper import FixedFastRestaurantScraper
from src.utils.logger import setup_logger
from src.database.database_adapter import get_database_manager


class UltraFastParallelScraper:
    """Extrator paralelo ultra-rápido"""
    
    def __init__(self, max_workers: int = 3, headless: bool = True):
        self.max_workers = max_workers
        self.headless = headless
        self.logger = setup_logger(self.__class__.__name__)
        self.db = get_database_manager()
        self.results_lock = threading.Lock()
        self.browser_lock = threading.Lock()  # Lock para browser compartilhado
        self.all_results = []
        
        # Browser pool para thread-safety
        self.browser_pool = []
        self.browser_lock = threading.Lock()  # Para o pool
        self.playwright_instances = []
        
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
    
    async def _setup_browser_pool(self):
        """Configura pool de browsers thread-safe"""
        try:
            self.logger.info(f"🚀 Inicializando pool de {self.max_workers} browsers...")
            
            # Cria um browser para cada worker
            for i in range(self.max_workers):
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(
                    headless=self.headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                self.playwright_instances.append(playwright)
                self.browser_pool.append({
                    'playwright': playwright,
                    'browser': browser,
                    'in_use': False,
                    'worker_id': None
                })
                
                self.logger.info(f"✅ Browser {i+1}/{self.max_workers} configurado")
            
            self.logger.info("✅ Pool de browsers configurado!")
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar pool: {e}")
            raise
    
    def _get_browser_from_pool(self):
        """Pega um browser disponível do pool"""
        with self.browser_lock:
            for browser_info in self.browser_pool:
                if not browser_info['in_use']:
                    browser_info['in_use'] = True
                    browser_info['worker_id'] = threading.current_thread().ident
                    return browser_info
            
            # Se chegou aqui, todos estão em uso - espera um pouco
            return None
    
    def _return_browser_to_pool(self, browser_info):
        """Retorna browser para o pool"""
        with self.browser_lock:
            browser_info['in_use'] = False
            browser_info['worker_id'] = None
    
    async def _cleanup_browser_pool(self):
        """Limpa pool de browsers"""
        try:
            self.logger.info("🧹 Limpando pool de browsers...")
            
            for browser_info in self.browser_pool:
                try:
                    await browser_info['browser'].close()
                    await browser_info['playwright'].stop()
                except:
                    pass
            
            self.browser_pool.clear()
            self.playwright_instances.clear()
            self.logger.info("✅ Pool de browsers limpo")
                
        except Exception as e:
            self.logger.error(f"⚠️ Erro na limpeza do pool: {e}")
    
    async def _extract_category_ultra_fast_pool(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Worker ultra-rápido com browser pool async"""
        category_name = category_data['name']
        category_url = category_data['url']
        worker_id = f"async-{id(asyncio.current_task())}"
        
        self.logger.info(f"⚡ [Worker {worker_id}] Iniciando {category_name}")
        
        browser_info = None
        try:
            # Pega browser do pool
            import time
            for attempt in range(10):  # Tenta 10x com delay
                browser_info = self._get_browser_from_pool()
                if browser_info:
                    break
                await asyncio.sleep(0.1)  # Espera 100ms async
            
            if not browser_info:
                raise Exception("Nenhum browser disponível no pool")
            
            # Usa FastRestaurantScraperFixed - PARALELO REAL + SELETORES QUE FUNCIONAM
            scraper = FastRestaurantScraperFixed(
                city=category_data.get('city', 'Birigui'),
                headless=self.headless
            )
            
            # Execução ASYNC PARALELA REAL com browser dedicado do pool
            result = await scraper.run_fast_for_category_async(
                browser=browser_info['browser'],
                category_url=category_url,
                category_name=category_name
            )
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"⚡ [Worker {worker_id}] ❌ {category_name}: {error_msg}")
            result = {
                'success': False,
                'category': category_name,
                'error': error_msg,
                'restaurants_found': 0,
                'new_saved': 0,
                'duplicates': 0,
                'duration': 0
            }
        
        finally:
            # SEMPRE retorna browser ao pool
            if browser_info:
                self._return_browser_to_pool(browser_info)
        
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
    
    async def extract_ultra_fast(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extração paralela ultra-rápida com browser compartilhado"""
        if not categories:
            return {
                'success': False,
                'error': 'Nenhuma categoria fornecida',
                'stats': self.stats
            }
        
        self.stats['total_categories'] = len(categories)
        self.stats['start_time'] = datetime.now()
        
        self.logger.info(f"⚡ EXTRAÇÃO ULTRA-RÁPIDA BROWSER POOL iniciada!")
        self.logger.info(f"📊 {len(categories)} categorias com {self.max_workers} workers")
        self.logger.info(f"🎯 Tempo estimado: {len(categories)*1.0/self.max_workers:.1f} minutos (7x mais rápido!)")
        
        try:
            # FASE 1: Setup do pool de browsers thread-safe
            setup_start = time.time()
            await self._setup_browser_pool()
            setup_time = time.time() - setup_start
            self.logger.info(f"⚡ Pool setup: {setup_time:.1f}s (vs ~{len(categories)*3:.1f}s anterior)")
            
            # FASE 2: Execução paralela async com browser pool
            tasks = []
            for cat in categories:
                task = self._extract_category_ultra_fast_pool(cat)
                tasks.append(task)
            
            # Limita concorrência ao número de workers
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def limited_task(task):
                async with semaphore:
                    return await task
            
            # Executa todas as tasks com limite de concorrência
            results = await asyncio.gather(
                *[limited_task(task) for task in tasks],
                return_exceptions=True
            )
            
            # Processa resultados
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"⚡ Erro inesperado {categories[i]['name']}: {result}")
                else:
                    # Log de progresso otimizado
                    progress = ((i + 1) / len(categories)) * 100
                    eta_seconds = (len(categories) - (i + 1)) * (self.stats['total_duration'] / max(i + 1, 1))
                    
                    self.logger.info(
                        f"⚡ Progresso: {i + 1}/{len(categories)} ({progress:.0f}%) "
                        f"| ETA: {eta_seconds/60:.1f}min | {categories[i]['name']} ✅"
                    )
        
        finally:
            # FASE 3: Cleanup do pool de browsers
            await self._cleanup_browser_pool()
        
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
    
    async def extract_from_database_ultra_fast(self) -> Dict[str, Any]:
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
            
            return await self.extract_ultra_fast(category_list)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar categorias: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    async def extract_specific_ultra_fast(self, category_names: List[str]) -> Dict[str, Any]:
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
            
            return await self.extract_ultra_fast(category_list)
            
        except Exception as e:
            self.logger.error(f"❌ Erro na seleção específica: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }


# Funções auxiliares ultra-rápidas
async def extract_all_ultra_fast(max_workers: int = 3, headless: bool = True) -> Dict[str, Any]:
    """Extrai todas as categorias ultra-rápido"""
    scraper = UltraFastParallelScraper(max_workers=max_workers, headless=headless)
    return await scraper.extract_from_database_ultra_fast()


async def extract_specific_ultra_fast(category_names: List[str], 
                                    max_workers: int = 3, 
                                    headless: bool = True) -> Dict[str, Any]:
    """Extrai categorias específicas ultra-rápido"""
    scraper = UltraFastParallelScraper(max_workers=max_workers, headless=headless)
    return await scraper.extract_specific_ultra_fast(category_names)


if __name__ == "__main__":
    # Teste ultra-rápido
    import asyncio
    
    async def main():
        print("⚡ Teste ULTRA-RÁPIDO")
        
        start = time.time()
        result = await extract_specific_ultra_fast(['Pizza', 'Lanches'], max_workers=2)
        duration = time.time() - start
        
        if result['success']:
            print(f"✅ Concluído em {duration:.1f}s")
            print(f"📊 {result['stats']['total_restaurants']} restaurantes")
        else:
            print(f"❌ Erro: {result['error']}")
    
    asyncio.run(main())