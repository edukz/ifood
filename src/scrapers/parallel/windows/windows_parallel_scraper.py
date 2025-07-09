#!/usr/bin/env python3
"""
Windows Parallel Scraper - Interface principal refatorada para scraping paralelo otimizado para Windows
"""

import asyncio
import platform
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.logger import setup_logger
from .windows_data_generator import WindowsDataGenerator
from .windows_data_processor import WindowsDataProcessor  
from .windows_database_manager import WindowsDatabaseManager


def detect_windows() -> bool:
    """Detecta se o sistema operacional é Windows"""
    return platform.system() == "Windows"


class WindowsParallelScraper:
    """Scraper paralelo otimizado para Windows - Interface principal refatorada"""
    
    def __init__(self, session_stats: Optional[Dict[str, Any]] = None):
        self.logger = setup_logger("WindowsParallelScraper")
        self.session_stats = session_stats or {}
        
        # Inicializar módulos especializados
        self.data_generator = WindowsDataGenerator()
        self.data_processor = WindowsDataProcessor()
        self.db_manager = WindowsDatabaseManager()
        
        # Configurar asyncio para Windows
        if detect_windows():
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                self.logger.info("Política de event loop do Windows configurada")
            except Exception as e:
                self.logger.warning(f"Erro ao configurar política do Windows: {e}")
        
        self.logger.info("WindowsParallelScraper inicializado com módulos especializados")
    
    async def extract_restaurants_parallel(self, categories: List[str], 
                                         restaurants_per_category: int = 50) -> Dict[str, Any]:
        """Extrai restaurantes de múltiplas categorias em paralelo"""
        start_time = datetime.now()
        
        self.logger.info(f"Iniciando extração paralela de restaurantes para {len(categories)} categorias")
        
        all_restaurants = []
        results_by_category = {}
        
        try:
            # Processar cada categoria
            for category in categories:
                self.logger.info(f"Extraindo restaurantes da categoria: {category}")
                
                # Gerar restaurantes usando o data_generator
                restaurants = self.data_generator._generate_restaurants_for_category(
                    category, restaurants_per_category
                )
                
                # Salvar restaurantes usando o db_manager
                save_results = self.db_manager._save_restaurants_to_mysql(restaurants)
                
                all_restaurants.extend(restaurants)
                results_by_category[category] = {
                    'restaurants_generated': len(restaurants),
                    'inserted': save_results['inserted'],
                    'updated': save_results['updated'],
                    'errors': save_results['errors']
                }
                
                self.logger.info(f"Categoria {category}: {len(restaurants)} restaurantes gerados")
            
            # Calcular estatísticas finais
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Atualizar estatísticas da sessão
            if self.session_stats:
                self.session_stats['restaurants_extracted'] = self.session_stats.get('restaurants_extracted', 0) + len(all_restaurants)
            
            results = {
                'success': True,
                'total_time': total_time,
                'total_restaurants': len(all_restaurants),
                'categories_processed': len(categories),
                'results_by_category': results_by_category,
                'performance': {
                    'restaurants_per_second': len(all_restaurants) / total_time if total_time > 0 else 0,
                    'categories_per_second': len(categories) / total_time if total_time > 0 else 0
                }
            }
            
            self.logger.info(f"Extração de restaurantes concluída em {total_time:.2f}s")
            self.logger.info(f"Total: {len(all_restaurants)} restaurantes de {len(categories)} categorias")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na extração paralela de restaurantes: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'total_time': (datetime.now() - start_time).total_seconds(),
                'total_restaurants': len(all_restaurants),
                'categories_processed': len(results_by_category),
                'results_by_category': results_by_category
            }
    
    async def extract_products_for_restaurant(self, restaurant_data: Dict[str, Any], 
                                            products_per_restaurant: int = 10) -> List[Dict[str, Any]]:
        """Extrai produtos para um restaurante específico"""
        return await self.data_processor.extract_products_for_restaurant(
            restaurant_data, products_per_restaurant
        )
    
    async def run_parallel_extraction(self, categories: List[str], 
                                    restaurants_per_category: int = 50,
                                    products_per_restaurant: int = 10) -> Dict[str, Any]:
        """Executa extração paralela completa (restaurantes + produtos)"""
        start_time = datetime.now()
        
        self.logger.info(f"Iniciando extração paralela completa para {len(categories)} categorias")
        
        try:
            # Usar o data_processor para coordenar a extração completa
            results = await self.data_processor.run_parallel_extraction(
                categories, restaurants_per_category, products_per_restaurant
            )
            
            # Atualizar estatísticas da sessão
            if self.session_stats and results.get('success'):
                self.session_stats['restaurants_extracted'] = self.session_stats.get('restaurants_extracted', 0) + results['restaurants']['total']
                self.session_stats['products_extracted'] = self.session_stats.get('products_extracted', 0) + results['products']['total']
            
            self.logger.info(f"Extração paralela completa concluída: {results}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na extração paralela completa: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'total_time': (datetime.now() - start_time).total_seconds(),
                'categories_processed': 0,
                'restaurants': {'total': 0},
                'products': {'total': 0}
            }
    
    def save_results(self, restaurants: List[Dict[str, Any]], 
                    products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Salva resultados usando o database manager"""
        return self.db_manager.save_results(restaurants, products)
    
    def load_existing_restaurants(self) -> List[Dict[str, Any]]:
        """Carrega restaurantes existentes do banco"""
        return self.db_manager._load_existing_restaurants_mysql()
    
    def load_existing_products(self) -> List[Dict[str, Any]]:
        """Carrega produtos existentes do banco"""
        return self.db_manager._load_existing_products_mysql()
    
    def get_supported_categories(self) -> List[str]:
        """Retorna lista de categorias suportadas"""
        return list(self.data_generator.restaurant_names_by_category.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do scraper"""
        try:
            restaurants = self.load_existing_restaurants()
            products = self.load_existing_products()
            
            # Agrupar por categoria
            restaurants_by_category = {}
            for restaurant in restaurants:
                category = restaurant.get('category', 'unknown')
                restaurants_by_category[category] = restaurants_by_category.get(category, 0) + 1
            
            return {
                'total_restaurants': len(restaurants),
                'total_products': len(products),
                'restaurants_by_category': restaurants_by_category,
                'supported_categories': self.get_supported_categories(),
                'session_stats': self.session_stats,
                'system_info': {
                    'platform': platform.system(),
                    'is_windows': detect_windows(),
                    'python_version': platform.python_version()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_restaurants': 0,
                'total_products': 0,
                'restaurants_by_category': {},
                'supported_categories': [],
                'session_stats': self.session_stats,
                'error': str(e)
            }
    
    async def process_single_category(self, category: str, 
                                    restaurants_per_category: int = 50,
                                    products_per_restaurant: int = 10) -> Dict[str, Any]:
        """Processa uma única categoria"""
        return await self.data_processor.process_single_category(
            category, restaurants_per_category, products_per_restaurant
        )
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Remove dados antigos do banco"""
        return self.db_manager.cleanup_old_data(days_old)
    
    def validate_category(self, category: str) -> bool:
        """Valida se uma categoria é suportada"""
        return category in self.get_supported_categories()
    
    def normalize_category(self, category: str) -> str:
        """Normaliza nome da categoria"""
        return self.data_generator._fix_incorrect_category(category)


# Função principal para compatibilidade com código existente
async def main():
    """Função principal para teste do scraper"""
    # Configurar asyncio para Windows
    if detect_windows():
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Criar instância do scraper
    scraper = WindowsParallelScraper()
    
    # Categorias de teste
    test_categories = ['pizza', 'hamburguer', 'japonesa']
    
    print(f"🚀 Iniciando teste do WindowsParallelScraper")
    print(f"📊 Sistema: {platform.system()}")
    print(f"🔧 Categorias de teste: {test_categories}")
    
    # Executar extração de teste
    results = await scraper.run_parallel_extraction(
        categories=test_categories,
        restaurants_per_category=10,
        products_per_restaurant=5
    )
    
    print(f"✅ Teste concluído:")
    print(f"   • Sucesso: {results.get('success', False)}")
    print(f"   • Tempo: {results.get('total_time', 0):.2f}s")
    print(f"   • Restaurantes: {results.get('restaurants', {}).get('total', 0)}")
    print(f"   • Produtos: {results.get('products', {}).get('total', 0)}")
    
    # Mostrar estatísticas
    stats = scraper.get_statistics()
    print(f"\n📈 Estatísticas do sistema:")
    print(f"   • Total de restaurantes: {stats['total_restaurants']}")
    print(f"   • Total de produtos: {stats['total_products']}")
    print(f"   • Categorias suportadas: {len(stats['supported_categories'])}")


if __name__ == "__main__":
    asyncio.run(main())