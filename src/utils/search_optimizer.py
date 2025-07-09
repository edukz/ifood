#!/usr/bin/env python3
"""
Search Optimizer - Interface compatível para sistema modular de busca otimizada
Sistema refatorado em módulos especializados para melhor manutenibilidade
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS
from .search import SearchDatabaseManager, SearchQueryEngine, SearchAnalyticsEngine
from .search.mysql_adapter import MySQLSearchAdapter


class SearchIndex:
    """Interface compatível para SearchDatabaseManager"""
    
    def __init__(self, index_dir: Path = None):
        self.database_manager = SearchDatabaseManager(index_dir)
        self.logger = setup_logger("SearchIndex")
    
    def create_database_indexes(self):
        """Cria banco SQLite com índices otimizados"""
        return self.database_manager.create_database_indexes()
    
    def load_data_to_database(self, data_dir: Path = None):
        """Carrega dados CSV para o banco SQLite"""
        return self.database_manager.load_data_to_database(data_dir)


class QueryOptimizer:
    """Interface compatível para sistema modular de busca otimizada"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.index_dir / "search_database.db"
        self.logger = setup_logger("QueryOptimizer")
        
        # Tentar usar MySQL, com fallback para SQLite
        self.mysql_adapter = None
        self.use_mysql = False
        
        try:
            self.mysql_adapter = MySQLSearchAdapter()
            self.use_mysql = True
            self.logger.info("Usando MySQL para busca em produção")
        except Exception as e:
            self.logger.warning(f"MySQL não disponível, usando SQLite: {e}")
            self.use_mysql = False
        
        # Inicializar módulos especializados (para compatibilidade com SQLite)
        self.database_manager = SearchDatabaseManager(self.index_dir)
        self.query_engine = SearchQueryEngine(self.index_dir)
        self.analytics_engine = SearchAnalyticsEngine(self.index_dir)
        
        # Inicializa banco de dados se não existir
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Garante que o banco de dados existe e está carregado com dados"""
        try:
            if not self.db_path.exists():
                self.logger.info("Banco de dados não encontrado. Criando...")
                self.database_manager.create_database_indexes()
                self.database_manager.load_data_to_database()
                self.logger.info("Banco de dados criado e carregado com sucesso")
            else:
                # Verifica se o banco tem dados
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM restaurants")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count == 0:
                    self.logger.info("Banco existe mas está vazio. Carregando dados...")
                    self.database_manager.load_data_to_database()
                    self.logger.info("Dados carregados no banco")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    # ==================== MÉTODOS DE BUSCA ====================
    
    def search_restaurants(self, 
                          query: str = None,
                          category: str = None,
                          min_rating: float = None,
                          max_delivery_fee: str = None,
                          city: str = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Busca otimizada de restaurantes"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.search_restaurants(
                query=query,
                category=category,
                min_rating=min_rating,
                city=city,
                limit=limit
            )
        else:
            return self.query_engine.search_restaurants(
                query=query,
                category=category,
                min_rating=min_rating,
                limit=limit
            )
    
    def search_products(self,
                       query: str = None,
                       category: str = None,
                       min_price: float = None,
                       max_price: float = None,
                       restaurant_id: str = None,
                       available_only: bool = True,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Busca otimizada de produtos"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.search_products(
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
                restaurant_id=restaurant_id,
                available_only=available_only,
                limit=limit
            )
        else:
            return self.query_engine.search_products(
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
                limit=limit
            )
    
    def search_by_location(self, city: str, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca restaurantes por localização"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.search_restaurants(city=city, category=category, limit=limit)
        else:
            return self.query_engine.search_restaurants(city=city, category=category, limit=limit)
    
    def get_recommendations(self, restaurant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em um restaurante"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.get_recommendations(restaurant_id, limit)
        else:
            return []  # Não implementado no SQLite
    
    def advanced_search(self, filters: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Busca avançada com múltiplos critérios"""
        return self.query_engine.advanced_search(filters)
    
    def search_with_fuzzy_matching(self, query: str, table: str = 'restaurants', 
                                  limit: int = 20) -> List[Dict[str, Any]]:
        """Busca com correspondência aproximada"""
        return self.query_engine.search_with_fuzzy_matching(query, table, limit)
    
    def get_trending_items(self, table: str = 'restaurants', limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna itens em tendência"""
        return self.query_engine.get_trending_items(table, limit)
    
    # ==================== MÉTODOS DE ANÁLISE ====================
    
    def get_popular_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna categorias mais populares"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.get_popular_categories(limit)
        else:
            return self.analytics_engine.get_popular_categories(limit)
    
    def get_price_distribution(self, category: str = None) -> Dict[str, int]:
        """Analisa distribuição de preços"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.get_price_distribution(category)
        else:
            return self.analytics_engine.get_price_distribution(category)
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do banco"""
        if self.use_mysql and self.mysql_adapter:
            return self.mysql_adapter.get_database_statistics()
        else:
            return self.database_manager.get_database_stats()
    
    def get_category_insights(self, category: str) -> Dict[str, Any]:
        """Obtém insights detalhados sobre uma categoria"""
        return self.analytics_engine.get_category_insights(category)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance do sistema"""
        return self.analytics_engine.get_performance_metrics()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Gera relatório resumido completo"""
        return self.analytics_engine.generate_summary_report()
    
    # ==================== MÉTODOS DE BANCO ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Método compatível - retorna estatísticas do banco"""
        return self.database_manager.get_database_stats()
    
    def create_database_indexes(self):
        """Método compatível - cria índices no banco"""
        return self.database_manager.create_database_indexes()
    
    def load_data_to_database(self, data_dir: Path = None):
        """Método compatível - carrega dados no banco"""
        return self.database_manager.load_data_to_database(data_dir)


# ==================== CLI INTERFACE ====================

def create_search_cli():
    """Interface de linha de comando para busca"""
    optimizer = QueryOptimizer()
    
    print("\n" + "="*60)
    print("SISTEMA DE BUSCA OTIMIZADA - MODULAR")
    print("="*60)
    
    while True:
        print("\nOpções:")
        print("1. Buscar restaurantes")
        print("2. Buscar produtos")
        print("3. Categorias populares")
        print("4. Análise de preços")
        print("5. Recomendações")
        print("6. Estatísticas completas")
        print("7. Busca avançada")
        print("0. Sair")
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            query = input("Buscar por nome/categoria: ").strip()
            min_rating = input("Avaliação mínima (Enter para qualquer): ").strip()
            min_rating = float(min_rating) if min_rating else None
            
            results = optimizer.search_restaurants(
                query=query if query else None,
                min_rating=min_rating
            )
            
            print(f"\n{len(results)} restaurantes encontrados:")
            for restaurant in results[:10]:
                print(f"  {restaurant['nome']} - {restaurant['categoria']} "
                      f"({restaurant['avaliacao']}⭐)")
        
        elif choice == "2":
            query = input("Buscar produto: ").strip()
            max_price = input("Preço máximo (Enter para qualquer): ").strip()
            max_price = float(max_price) if max_price else None
            
            results = optimizer.search_products(
                query=query if query else None,
                max_price=max_price
            )
            
            print(f"\n{len(results)} produtos encontrados:")
            for product in results[:10]:
                print(f"  {product['nome']} - {product['preco']} "
                      f"({product['restaurant_name']})")
        
        elif choice == "3":
            categories = optimizer.get_popular_categories()
            print("\nCategorias mais populares:")
            for cat in categories:
                print(f"  {cat['categoria']}: {cat['restaurant_count']} restaurantes "
                      f"(⭐{cat['avg_rating']})")
        
        elif choice == "4":
            category = input("Categoria (Enter para todas): ").strip()
            distribution = optimizer.get_price_distribution(
                category if category else None
            )
            
            print("\nDistribuição de preços:")
            for range_name, count in distribution.items():
                print(f"  {range_name}: {count} produtos")
        
        elif choice == "5":
            restaurant_id = input("ID do restaurante: ").strip()
            recommendations = optimizer.get_recommendations(restaurant_id)
            
            print("\nRecomendações:")
            for rec in recommendations:
                print(f"  {rec['nome']} - {rec['categoria']} ({rec['avaliacao']}⭐)")
        
        elif choice == "6":
            stats = optimizer.get_database_statistics()
            print("\nEstatísticas do Sistema:")
            print(f"  Restaurantes: {stats.get('total_restaurants', 0)}")
            print(f"  Produtos: {stats.get('total_products', 0)}")
            print(f"  Categorias: {stats.get('total_categories', 0)}")
            
            if 'price_stats' in stats:
                price_stats = stats['price_stats']
                print(f"  Preço médio: R$ {price_stats.get('avg_price', 0)}")
                print(f"  Preço máximo: R$ {price_stats.get('max_price', 0)}")
        
        elif choice == "7":
            print("\nBusca Avançada:")
            query = input("Termo de busca: ").strip()
            filters = {
                'query': query if query else None,
                'min_rating': None,
                'city': None
            }
            
            city = input("Cidade (Enter para qualquer): ").strip()
            if city:
                filters['city'] = city
            
            results = optimizer.advanced_search(filters)
            
            print(f"\nResultados da busca avançada:")
            print(f"  Restaurantes: {len(results['restaurants'])}")
            print(f"  Produtos: {len(results['products'])}")
        
        elif choice == "0":
            break


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de busca otimizada modular")
    parser.add_argument("--create-db", action="store_true",
                       help="Criar banco de dados com índices")
    parser.add_argument("--load-data", action="store_true", 
                       help="Carregar dados CSV no banco")
    parser.add_argument("--cli", action="store_true",
                       help="Interface de busca interativa")
    
    args = parser.parse_args()
    
    if args.create_db:
        index = SearchIndex()
        index.create_database_indexes()
        
    if args.load_data:
        index = SearchIndex()
        index.load_data_to_database()
        
    if args.cli:
        create_search_cli()
        
    if not any([args.create_db, args.load_data, args.cli]):
        print("Sistema de Busca Otimizada - Modular")
        print("Use --help para ver opções disponíveis")
        
        # Executa setup básico
        index = SearchIndex()
        index.create_database_indexes()
        index.load_data_to_database()