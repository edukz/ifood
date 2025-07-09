#!/usr/bin/env python3
"""
Sistema de Paralelismo Nativo para Windows - Interface Compatível com Sistema Modular
"""

import asyncio
import time
import platform
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.utils.logger import setup_logger
from src.database.database_adapter import get_database_manager
from .windows import WindowsParallelScraper as ModularWindowsParallelScraper, detect_windows


class WindowsParallelScraper:
    """Interface compatível para o scraper paralelo modular do Windows"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results = []
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.logger = setup_logger(self.__class__.__name__)
        
        # Inicializa Database Manager V2
        self.db_manager = get_database_manager()
        
        # Criar instância do scraper modular
        self.modular_scraper = ModularWindowsParallelScraper()
        
        # Carrega dados reais existentes do MySQL (compatibilidade)
        self.restaurants_data = self._load_existing_restaurants_mysql()
        self.products_templates = self._load_existing_products_mysql()
        
        print(f"🪟 Sistema Windows Nativo Iniciado - 100% MySQL")
        print(f"📊 Dados carregados: {len(self.restaurants_data)} restaurantes, {len(self.products_templates)} produtos template")
        print(f"🗄️ Sistema de deduplicação MySQL ativo")
        print(f"🔧 Sistema modular carregado com {len(self.modular_scraper.get_supported_categories())} categorias")
    
    def extract_restaurants_parallel(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai restaurantes para categorias específicas usando o sistema modular"""
        start_time = time.time()
        
        self.logger.info(f"Iniciando extração paralela de restaurantes para {len(categories)} categorias")
        
        try:
            # Converter formato de categorias para o sistema modular
            category_names = []
            for category in categories:
                if isinstance(category, dict):
                    category_name = category.get('name', category.get('category', 'geral'))
                else:
                    category_name = str(category)
                
                # Normalizar categoria
                normalized_category = self.modular_scraper.normalize_category(category_name)
                category_names.append(normalized_category)
            
            # Usar o sistema modular
            async def run_extraction():
                return await self.modular_scraper.extract_restaurants_parallel(
                    category_names, restaurants_per_category=50
                )
            
            # Executar extração
            if detect_windows():
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            results = asyncio.run(run_extraction())
            
            # Formatar resultados no formato esperado
            formatted_results = {
                'success': results.get('success', False),
                'total_time': results.get('total_time', 0),
                'total_restaurants_extracted': results.get('total_restaurants', 0),
                'categories_processed': results.get('categories_processed', 0),
                'restaurants_per_category': results.get('results_by_category', {}),
                'performance_metrics': results.get('performance', {}),
                'system_info': {
                    'platform': platform.system(),
                    'is_windows': detect_windows(),
                    'modular_system': True
                }
            }
            
            self.logger.info(f"Extração paralela concluída em {results.get('total_time', 0):.2f}s")
            self.logger.info(f"Total: {results.get('total_restaurants', 0)} restaurantes")
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Erro na extração paralela: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'total_time': time.time() - start_time,
                'total_restaurants_extracted': 0,
                'categories_processed': 0,
                'restaurants_per_category': {},
                'performance_metrics': {},
                'system_info': {
                    'platform': platform.system(),
                    'is_windows': detect_windows(),
                    'modular_system': True
                }
            }
    
    async def extract_products_for_restaurant(self, restaurant_data: Dict[str, Any], 
                                            products_per_restaurant: int = 10) -> List[Dict[str, Any]]:
        """Extrai produtos para um restaurante específico"""
        return await self.modular_scraper.extract_products_for_restaurant(
            restaurant_data, products_per_restaurant
        )
    
    def save_results(self, restaurants: List[Dict[str, Any]], 
                    products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Salva resultados usando o sistema modular"""
        return self.modular_scraper.save_results(restaurants, products)
    
    def _load_existing_restaurants_mysql(self) -> List[Dict[str, Any]]:
        """Carrega restaurantes existentes do MySQL (compatibilidade)"""
        return self.modular_scraper.load_existing_restaurants()
    
    def _load_existing_products_mysql(self) -> List[Dict[str, Any]]:
        """Carrega produtos existentes do MySQL (compatibilidade)"""
        return self.modular_scraper.load_existing_products()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do scraper"""
        return self.modular_scraper.get_statistics()
    
    def get_supported_categories(self) -> List[str]:
        """Retorna categorias suportadas"""
        return self.modular_scraper.get_supported_categories()
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Remove dados antigos"""
        return self.modular_scraper.cleanup_old_data(days_old)
    
    # Métodos de compatibilidade com código antigo
    def _get_restaurant_names_by_category(self, category: str) -> List[str]:
        """Método de compatibilidade"""
        return self.modular_scraper.data_generator._get_restaurant_names_by_category(category)
    
    def _generate_restaurants_for_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Método de compatibilidade"""
        return self.modular_scraper.data_generator._generate_restaurants_for_category(category, limit)
    
    def _generate_realistic_product_name(self, category: str) -> str:
        """Método de compatibilidade"""
        return self.modular_scraper.data_generator._generate_realistic_product_name(category)
    
    def _generate_realistic_description(self, product_name: str, category: str) -> str:
        """Método de compatibilidade"""
        return self.modular_scraper.data_generator._generate_realistic_description(product_name, category)
    
    def _generate_realistic_price_by_category(self, category: str) -> float:
        """Método de compatibilidade"""
        return self.modular_scraper.data_generator._generate_realistic_price_by_category(category)


# Função principal para compatibilidade
async def main():
    """Função principal para teste do scraper"""
    # Configurar asyncio para Windows
    if detect_windows():
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Criar instância do scraper
    scraper = WindowsParallelScraper()
    
    # Categorias de teste
    test_categories = [
        {'name': 'pizza'},
        {'name': 'hamburguer'},
        {'name': 'japonesa'}
    ]
    
    print(f"🚀 Iniciando teste do WindowsParallelScraper")
    print(f"📊 Sistema: {platform.system()}")
    print(f"🔧 Categorias de teste: {[cat['name'] for cat in test_categories]}")
    
    # Executar extração de teste
    results = scraper.extract_restaurants_parallel(test_categories)
    
    print(f"✅ Teste concluído:")
    print(f"   • Sucesso: {results.get('success', False)}")
    print(f"   • Tempo: {results.get('total_time', 0):.2f}s")
    print(f"   • Restaurantes: {results.get('total_restaurants_extracted', 0)}")
    print(f"   • Categorias: {results.get('categories_processed', 0)}")
    
    # Mostrar estatísticas
    stats = scraper.get_statistics()
    print(f"\n📈 Estatísticas do sistema:")
    print(f"   • Total de restaurantes: {stats['total_restaurants']}")
    print(f"   • Total de produtos: {stats['total_products']}")
    print(f"   • Categorias suportadas: {len(stats['supported_categories'])}")


if __name__ == "__main__":
    asyncio.run(main())