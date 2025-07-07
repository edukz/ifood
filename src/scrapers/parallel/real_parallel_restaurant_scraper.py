#!/usr/bin/env python3
"""
Real Parallel Restaurant Scraper
Sistema de paralelismo real baseado no RestaurantScraper
Usa múltiplos browsers para coleta eficiente e real
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading

try:
    from playwright.sync_api import Playwright, sync_playwright, TimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    class Playwright:
        pass
    class TimeoutError(Exception):
        pass

from src.scrapers.restaurant_scraper import RestaurantScraper
from src.database.database_adapter import get_database_manager
from src.utils.logger import setup_logger
from src.models.restaurant import Restaurant
from src.utils.colors import color_printer as cp, print_success, print_error, print_warning, print_info, print_action, print_phase, print_progress
# Deduplication is now handled internally by DatabaseManagerV2


@dataclass
class ScrapingTask:
    """Tarefa de scraping para uma categoria"""
    category_name: str
    category_url: str
    city: str
    task_id: int


@dataclass
class ScrapingResult:
    """Resultado do scraping de uma categoria"""
    task_id: int
    category_name: str
    success: bool
    restaurants_count: int
    new_saved: int
    duplicates: int
    execution_time: float
    error_message: Optional[str] = None


class WorkerScraper(RestaurantScraper):
    """Scraper worker otimizado para execução paralela"""
    
    def __init__(self, worker_id: int, city: str = "Birigui"):
        super().__init__(city, headless=True)  # Sempre headless no paralelo
        self.worker_id = worker_id
        self.logger = setup_logger(f"Worker-{worker_id}")
        # DatabaseManagerV2 handles deduplication internally
        
    def scrape_category(self, task: ScrapingTask) -> ScrapingResult:
        """Executa scraping de uma categoria específica"""
        start_time = time.time()
        
        try:
            print_action(f"WORKER {self.worker_id}", cp.category(task.category_name))
            
            # Navega para a categoria
            self.navigate_to_category(task.category_url, task.category_name)
            
            # Extrai restaurantes
            self.extract_restaurants()
            
            # 🎯 Adiciona restaurantes ao deduplicador em vez de salvar diretamente
            if self.restaurants:
                restaurants_count = len(self.restaurants)
                
                try:
                    # Converte restaurantes para formato dict
                    restaurants_data = []
                    for rest in self.restaurants:
                        if hasattr(rest, 'to_dict'):
                            rest_dict = rest.to_dict()
                        else:
                            rest_dict = dict(rest) if rest else {}
                        
                        # Debug: verifica dados válidos
                        if not rest_dict or not rest_dict.get('nome'):
                            self.logger.warning(f"[Worker {self.worker_id}] ⚠️ Restaurante inválido ignorado: {rest_dict}")
                            continue
                        
                        restaurants_data.append(rest_dict)
                    
                    if not restaurants_data:
                        self.logger.warning(f"[Worker {self.worker_id}] ⚠️ Nenhum restaurante válido encontrado")
                        restaurants_count = 0
                        new_saved = 0
                        duplicates = 0
                    else:
                        # Save restaurants directly - DatabaseManagerV2 handles deduplication
                        save_result = self.save_restaurants()
                        new_saved = save_result.get('inserted', 0)
                        duplicates = save_result.get('updated', 0)
                        
                        print_success(f"[Worker {self.worker_id}] {cp.category(task.category_name)}: {cp.stats('Coletados', str(restaurants_count))} | {cp.stats('Novos', str(new_saved))} | {cp.stats('Atualizados', str(duplicates))}", bold=False)
                
                except Exception as e:
                    self.logger.error(f"[Worker {self.worker_id}] ❌ Erro ao processar restaurantes: {e}")
                    raise e
            else:
                restaurants_count = 0
                new_saved = 0
                duplicates = 0
                print_warning(f"[Worker {self.worker_id}] {cp.category(task.category_name)}: Nenhum restaurante encontrado")
            
            execution_time = time.time() - start_time
            
            return ScrapingResult(
                task_id=task.task_id,
                category_name=task.category_name,
                success=True,
                restaurants_count=restaurants_count,
                new_saved=new_saved,
                duplicates=duplicates,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            print_error(f"[Worker {self.worker_id}] {cp.category(task.category_name)}: {error_msg}")
            
            return ScrapingResult(
                task_id=task.task_id,
                category_name=task.category_name,
                success=False,
                restaurants_count=0,
                new_saved=0,
                duplicates=0,
                execution_time=execution_time,
                error_message=error_msg
            )
        
        finally:
            # Limpa dados para próxima tarefa
            self.restaurants = []
            self.current_category = None


class RealParallelRestaurantScraper:
    """Sistema de scraping paralelo real com pool de browsers"""
    
    def __init__(self, max_workers: int = 3, city: str = "Birigui"):
        self.max_workers = max_workers
        self.city = city
        self.logger = setup_logger("RealParallelScraper")
        self.db = get_database_manager()
        
        # Estatísticas
        self.stats = {
            'total_categories': 0,
            'successful_categories': 0,
            'failed_categories': 0,
            'total_restaurants': 0,
            'total_new_saved': 0,
            'total_duplicates': 0,
            'memory_duplicates': 0,
            'total_time': 0,
            'start_time': None,
            'results': []
        }
    
    def setup_browser_pool(self) -> List[WorkerScraper]:
        """Cria pool de scrapers workers"""
        print_phase(f"Criando pool de {self.max_workers} workers")
        
        workers = []
        for worker_id in range(self.max_workers):
            try:
                worker = WorkerScraper(worker_id, self.city)
                # Inicializa o worker (setup do browser)
                with sync_playwright() as playwright:
                    worker.setup_browser(playwright)
                workers.append(worker)
                print_success(f"Worker {worker_id} criado")
            except Exception as e:
                print_error(f"Erro ao criar Worker {worker_id}: {e}")
        
        print_info(f"Pool criado com {len(workers)} workers ativos", bold=True)
        return workers
    
    def prepare_tasks(self, categories: List[Dict[str, Any]]) -> List[ScrapingTask]:
        """Prepara tarefas de scraping"""
        tasks = []
        
        for i, category in enumerate(categories):
            task = ScrapingTask(
                category_name=category.get('name', f'Categoria_{i}'),
                category_url=category.get('url', ''),
                city=self.city,
                task_id=i
            )
            tasks.append(task)
        
        print_info(f"Preparadas {len(tasks)} tarefas de scraping", bold=True)
        return tasks
    
    def worker_function(self, worker_scraper: WorkerScraper, task: ScrapingTask) -> ScrapingResult:
        """Função executada por cada worker"""
        thread_name = threading.current_thread().name
        self.logger.info(f"[{thread_name}] Executando tarefa {task.task_id}: {task.category_name}")
        
        try:
            # Cada worker precisa do seu próprio browser
            with sync_playwright() as playwright:
                worker_scraper.setup_browser(playwright)
                result = worker_scraper.scrape_category(task)
                worker_scraper.browser.close()
                return result
        except Exception as e:
            self.logger.error(f"[{thread_name}] Erro no worker: {e}")
            return ScrapingResult(
                task_id=task.task_id,
                category_name=task.category_name,
                success=False,
                restaurants_count=0,
                new_saved=0,
                duplicates=0,
                execution_time=0,
                error_message=str(e)
            )
    
    def scrape_parallel(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa scraping paralelo de múltiplas categorias"""
        self.stats['start_time'] = time.time()
        self.stats['total_categories'] = len(categories)
        
        print_phase(f"Iniciando scraping paralelo de {len(categories)} categorias")
        print_info(f"Configuração: {self.max_workers} workers, cidade: {self.city}", bold=True)
        
        # Prepara tarefas
        tasks = self.prepare_tasks(categories)
        
        # Executa em paralelo usando ThreadPoolExecutor
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="ScraperWorker") as executor:
            # Submit todas as tarefas
            future_to_task = {}
            
            for task in tasks:
                # Cria um worker específico para esta tarefa
                worker = WorkerScraper(task.task_id, self.city)
                future = executor.submit(self.worker_function, worker, task)
                future_to_task[future] = task
            
            # Coleta resultados conforme completam
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Atualiza estatísticas
                    if result.success:
                        self.stats['successful_categories'] += 1
                        self.stats['total_restaurants'] += result.restaurants_count
                        # ⚠️ NÃO soma aqui - será calculado no final baseado na deduplicação real
                        status = "✅"
                    else:
                        self.stats['failed_categories'] += 1
                        status = "❌"
                    
                    progress = len(results)
                    total = len(tasks)
                    
                    self.logger.info(
                        f"{status} [{progress}/{total}] {result.category_name}: "
                        f"{result.restaurants_count} coletados ({result.new_saved} novos, {result.duplicates} duplicados) em {result.execution_time:.1f}s"
                    )
                    
                except Exception as e:
                    self.logger.error(f"Erro ao processar resultado da tarefa {task.category_name}: {e}")
        
        # Finaliza estatísticas
        self.stats['total_time'] = time.time() - self.stats['start_time']
        self.stats['results'] = results
        
        # Calculate final statistics from results
        for result in results:
            if result.success:
                self.stats['total_new_saved'] += result.new_saved
                self.stats['total_duplicates'] += result.duplicates
        
        return self._generate_summary()
    
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Gera resumo dos resultados"""
        
        summary = {
            'total_categories': self.stats['total_categories'],
            'successful_categories': self.stats['successful_categories'],
            'failed_categories': self.stats['failed_categories'],
            'total_restaurants': self.stats['total_restaurants'],
            'total_new_saved': self.stats['total_new_saved'],  # ✅ INSERTs reais no banco
            'total_updated': self.stats['total_duplicates'],   # ✅ UPDATEs reais no banco  
            'total_duplicates': self.stats['total_duplicates'], # ✅ Restaurantes atualizados
            'unique_restaurants': self.stats['total_restaurants'] - self.stats['total_duplicates'],  # ✅ Restaurantes únicos processados
            'total_time': self.stats['total_time'],
            'avg_time_per_category': self.stats['total_time'] / max(self.stats['total_categories'], 1),
            'restaurants_per_minute': (self.stats['total_restaurants'] / self.stats['total_time'] * 60) if self.stats['total_time'] > 0 else 0,
            'success_rate': (self.stats['successful_categories'] / max(self.stats['total_categories'], 1)) * 100,
            'results': self.stats['results']
        }
        
        print(f"\n{cp.highlight('📊 RESUMO DO SCRAPING PARALELO:', bold=True)}")
        sucessos_text = f"{summary['successful_categories']}/{summary['total_categories']}"
        print(f"  {cp.stats('Sucessos', sucessos_text)}")
        print(f"  {cp.stats('Restaurantes coletados', str(summary['total_restaurants']))}")
        print(f"  {cp.stats('Restaurantes únicos', str(summary['unique_restaurants']))}")
        print(f"  {cp.stats('Novos salvos', str(summary['total_new_saved']))}")
        print(f"  {cp.stats('Atualizados', str(summary['total_duplicates']))}")
        tempo_text = f"{summary['total_time']:.1f}s"
        print(f"  {cp.stats('Tempo total', tempo_text, good=True)}")
        performance_text = f"{summary['restaurants_per_minute']:.1f} rest/min"
        print(f"  {cp.stats('Performance', performance_text, good=True)}")
        taxa_text = f"{summary['success_rate']:.1f}%"
        print(f"  {cp.stats('Taxa de sucesso', taxa_text, good=summary['success_rate'] > 90)}")
        
        # 📋 RESUMO DETALHADO POR CATEGORIA
        self.logger.info("📋 DETALHAMENTO POR CATEGORIA:")
        for result in self.stats['results']:
            if result.success:
                status = "✅"
                details = f"{result.restaurants_count} coletados, {result.new_saved} novos, {result.duplicates} duplicados"
            else:
                status = "❌"
                details = f"FALHA - {result.error_message}"
            
            self.logger.info(f"  {status} {result.category_name}: {details} ({result.execution_time:.1f}s)")
        
        self.logger.info("═" * 60)
        
        return summary


def main():
    """Função de teste"""
    scraper = RealParallelRestaurantScraper(max_workers=2)
    
    # Categorias de teste
    test_categories = [
        {'name': 'Pizza', 'url': 'https://www.ifood.com.br/delivery/birigui-sp/pizza'},
        {'name': 'Lanches', 'url': 'https://www.ifood.com.br/delivery/birigui-sp/lanches'}
    ]
    
    results = scraper.scrape_parallel(test_categories)
    print("\n🎯 Teste concluído!")
    print(f"Restaurantes coletados: {results['total_restaurants']}")


if __name__ == "__main__":
    main()