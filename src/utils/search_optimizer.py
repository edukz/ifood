"""
Sistema de otimização de consultas e índices para busca rápida
Acelera buscas em grandes volumes de dados
"""

import csv
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict
import sqlite3
from datetime import datetime
import re

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


class SearchIndex:
    """Índice de busca otimizado para dados do scraper"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger("SearchIndex")
        
        # Índices em memória
        self.name_index = defaultdict(list)  # Nome → registros
        self.category_index = defaultdict(list)  # Categoria → registros
        self.price_index = defaultdict(list)  # Faixa de preço → registros
        self.city_index = defaultdict(list)  # Cidade → registros
        self.rating_index = defaultdict(list)  # Rating → registros
        
        # Metadados dos índices
        self.index_metadata = {
            'last_updated': None,
            'total_records': 0,
            'data_sources': []
        }
    
    def create_database_indexes(self):
        """Cria banco SQLite com índices otimizados"""
        db_path = self.index_dir / "search_database.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Tabela de restaurantes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS restaurants (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    avaliacao REAL,
                    tempo_entrega TEXT,
                    taxa_entrega TEXT,
                    distancia TEXT,
                    url TEXT,
                    endereco TEXT,
                    city TEXT,
                    extracted_at TEXT
                )
            """)
            
            # Tabela de produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    preco_numerico REAL,
                    preco TEXT,
                    preco_original TEXT,
                    categoria_produto TEXT,
                    disponivel BOOLEAN,
                    imagem_url TEXT,
                    tempo_preparo TEXT,
                    serve_pessoas INTEGER,
                    calorias TEXT,
                    tags TEXT,
                    restaurant_id TEXT,
                    restaurant_name TEXT,
                    extracted_at TEXT,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
                )
            """)
            
            # Tabela de categorias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT,
                    slug TEXT,
                    city TEXT,
                    icon TEXT,
                    extracted_at TEXT
                )
            """)
            
            # Índices para busca rápida
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_restaurants_nome ON restaurants (nome)",
                "CREATE INDEX IF NOT EXISTS idx_restaurants_categoria ON restaurants (categoria)",
                "CREATE INDEX IF NOT EXISTS idx_restaurants_avaliacao ON restaurants (avaliacao)",
                "CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants (city)",
                
                "CREATE INDEX IF NOT EXISTS idx_products_nome ON products (nome)",
                "CREATE INDEX IF NOT EXISTS idx_products_preco ON products (preco_numerico)",
                "CREATE INDEX IF NOT EXISTS idx_products_categoria ON products (categoria_produto)",
                "CREATE INDEX IF NOT EXISTS idx_products_restaurant ON products (restaurant_id)",
                "CREATE INDEX IF NOT EXISTS idx_products_disponivel ON products (disponivel)",
                
                "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name)",
                "CREATE INDEX IF NOT EXISTS idx_categories_city ON categories (city)",
                
                # Índices compostos para consultas complexas
                "CREATE INDEX IF NOT EXISTS idx_restaurants_categoria_avaliacao ON restaurants (categoria, avaliacao DESC)",
                "CREATE INDEX IF NOT EXISTS idx_products_categoria_preco ON products (categoria_produto, preco_numerico)",
                "CREATE INDEX IF NOT EXISTS idx_products_restaurant_categoria ON products (restaurant_id, categoria_produto)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            self.logger.info("Banco de dados com índices criado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar banco de dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def load_data_to_database(self, data_dir: Path = None):
        """Carrega dados CSV para o banco SQLite"""
        data_dir = data_dir or Path(SETTINGS.output_dir)
        db_path = self.index_dir / "search_database.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Limpa dados existentes
            cursor.execute("DELETE FROM restaurants")
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM categories")
            
            # Carrega categorias
            categories_dir = data_dir / "categories"
            if categories_dir.exists():
                for csv_file in categories_dir.glob("*.csv"):
                    self._load_csv_to_table(csv_file, "categories", cursor)
            
            # Carrega restaurantes
            restaurants_dir = data_dir / "restaurants"
            if restaurants_dir.exists():
                for csv_file in restaurants_dir.glob("*.csv"):
                    self._load_csv_to_table(csv_file, "restaurants", cursor)
            
            # Carrega produtos
            products_dir = data_dir / "products"
            if products_dir.exists():
                for csv_file in products_dir.glob("*.csv"):
                    self._load_csv_to_table(csv_file, "products", cursor)
            
            conn.commit()
            
            # Atualiza estatísticas
            self._update_database_stats(cursor)
            
            self.logger.info("Dados carregados no banco com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _load_csv_to_table(self, csv_file: Path, table_name: str, cursor):
        """Carrega um arquivo CSV específico para uma tabela"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if table_name == "products":
                        # Converte preço para número para busca numérica
                        preco_str = row.get('preco', '').replace('R$', '').replace(' ', '').replace(',', '.')
                        try:
                            row['preco_numerico'] = float(preco_str) if preco_str and preco_str != 'Não informado' else 0
                        except ValueError:
                            row['preco_numerico'] = 0
                    
                    # Prepare os dados baseado na tabela
                    if table_name == "restaurants":
                        placeholders = ",".join(["?" for _ in range(11)])
                        cursor.execute(f"""
                            INSERT OR REPLACE INTO {table_name} 
                            (id, nome, categoria, avaliacao, tempo_entrega, taxa_entrega, 
                             distancia, url, endereco, city, extracted_at)
                            VALUES ({placeholders})
                        """, (
                            row.get('id', ''),
                            row.get('nome', ''),
                            row.get('categoria', ''),
                            float(row.get('avaliacao', 0)) if row.get('avaliacao') else None,
                            row.get('tempo_entrega', ''),
                            row.get('taxa_entrega', ''),
                            row.get('distancia', ''),
                            row.get('url', ''),
                            row.get('endereco', ''),
                            row.get('city', ''),
                            row.get('extracted_at', '')
                        ))
                    
                    elif table_name == "products":
                        placeholders = ",".join(["?" for _ in range(16)])
                        cursor.execute(f"""
                            INSERT OR REPLACE INTO {table_name}
                            (id, nome, descricao, preco_numerico, preco, preco_original,
                             categoria_produto, disponivel, imagem_url, tempo_preparo,
                             serve_pessoas, calorias, tags, restaurant_id, restaurant_name, extracted_at)
                            VALUES ({placeholders})
                        """, (
                            row.get('id', ''),
                            row.get('nome', ''),
                            row.get('descricao', ''),
                            row.get('preco_numerico', 0),
                            row.get('preco', ''),
                            row.get('preco_original', ''),
                            row.get('categoria_produto', ''),
                            row.get('disponivel', '').lower() == 'true',
                            row.get('imagem_url', ''),
                            row.get('tempo_preparo', ''),
                            int(row.get('serve_pessoas', 0)) if row.get('serve_pessoas') else None,
                            row.get('calorias', ''),
                            row.get('tags', ''),
                            row.get('restaurant_id', ''),
                            row.get('restaurant_name', ''),
                            row.get('extracted_at', '')
                        ))
                    
                    elif table_name == "categories":
                        placeholders = ",".join(["?" for _ in range(6)])
                        cursor.execute(f"""
                            INSERT OR REPLACE INTO {table_name}
                            (id, name, url, slug, city, icon, extracted_at)
                            VALUES ({placeholders})
                        """, (
                            row.get('id', ''),
                            row.get('name', ''),
                            row.get('url', ''),
                            row.get('slug', ''),
                            row.get('city', ''),
                            row.get('icon', ''),
                            row.get('extracted_at', '')
                        ))
        
        except Exception as e:
            self.logger.error(f"Erro ao carregar {csv_file}: {e}")
    
    def _update_database_stats(self, cursor):
        """Atualiza estatísticas do banco"""
        try:
            cursor.execute("SELECT COUNT(*) FROM restaurants")
            restaurants_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            products_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM categories")
            categories_count = cursor.fetchone()[0]
            
            self.logger.info(f"Estatísticas do banco:")
            self.logger.info(f"  Restaurantes: {restaurants_count}")
            self.logger.info(f"  Produtos: {products_count}")
            self.logger.info(f"  Categorias: {categories_count}")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas: {e}")


class QueryOptimizer:
    """Otimizador de consultas para buscas complexas"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.index_dir / "search_database.db"
        self.logger = setup_logger("QueryOptimizer")
        
        # Inicializa banco de dados se não existir
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Garante que o banco de dados existe e está carregado com dados"""
        try:
            if not self.db_path.exists():
                self.logger.info("Banco de dados não encontrado. Criando...")
                # Cria o banco e carrega dados
                search_index = SearchIndex(self.index_dir)
                search_index.create_database_indexes()
                search_index.load_data_to_database()
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
                    search_index = SearchIndex(self.index_dir)
                    search_index.load_data_to_database()
                    self.logger.info("Dados carregados no banco")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    def search_restaurants(self, 
                          query: str = None,
                          category: str = None,
                          min_rating: float = None,
                          max_delivery_fee: str = None,
                          city: str = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Busca otimizada de restaurantes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        try:
            # Constrói query SQL otimizada
            sql = "SELECT * FROM restaurants WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (nome LIKE ? OR categoria LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND categoria = ?"
                params.append(category)
            
            if min_rating is not None:
                sql += " AND avaliacao >= ?"
                params.append(min_rating)
            
            if city:
                sql += " AND city = ?"
                params.append(city)
            
            if max_delivery_fee and max_delivery_fee != "Grátis":
                # Implementar lógica para taxa de entrega
                pass
            
            # Ordena por avaliação e limita resultados
            sql += " ORDER BY avaliacao DESC, nome ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            self.logger.debug(f"Busca de restaurantes retornou {len(results)} resultados")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca de restaurantes: {e}")
            return []
        finally:
            conn.close()
    
    def search_products(self,
                       query: str = None,
                       category: str = None,
                       min_price: float = None,
                       max_price: float = None,
                       restaurant_id: str = None,
                       available_only: bool = True,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Busca otimizada de produtos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            sql = "SELECT * FROM products WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (nome LIKE ? OR descricao LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND categoria_produto = ?"
                params.append(category)
            
            if min_price is not None:
                sql += " AND preco_numerico >= ?"
                params.append(min_price)
            
            if max_price is not None:
                sql += " AND preco_numerico <= ?"
                params.append(max_price)
            
            if restaurant_id:
                sql += " AND restaurant_id = ?"
                params.append(restaurant_id)
            
            if available_only:
                sql += " AND disponivel = 1"
            
            # Ordena por preço e limita
            sql += " ORDER BY preco_numerico ASC, nome ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            self.logger.debug(f"Busca de produtos retornou {len(results)} resultados")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca de produtos: {e}")
            return []
        finally:
            conn.close()
    
    def get_popular_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna categorias mais populares por número de restaurantes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT categoria, COUNT(*) as restaurant_count,
                       AVG(avaliacao) as avg_rating
                FROM restaurants 
                WHERE categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria 
                ORDER BY restaurant_count DESC, avg_rating DESC
                LIMIT ?
            """
            
            cursor.execute(sql, (limit,))
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    'categoria': row[0],
                    'restaurant_count': row[1],
                    'avg_rating': round(row[2], 2) if row[2] else 0
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar categorias populares: {e}")
            return []
        finally:
            conn.close()
    
    def get_price_distribution(self, category: str = None) -> Dict[str, int]:
        """Analisa distribuição de preços"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            sql = "SELECT preco_numerico FROM products WHERE preco_numerico > 0"
            params = []
            
            if category:
                sql += " AND categoria_produto = ?"
                params.append(category)
            
            cursor.execute(sql, params)
            prices = [row[0] for row in cursor.fetchall()]
            
            if not prices:
                return {}
            
            # Cria faixas de preço
            distribution = {
                "Até R$ 10": 0,
                "R$ 10-20": 0,
                "R$ 20-50": 0,
                "R$ 50-100": 0,
                "Acima R$ 100": 0
            }
            
            for price in prices:
                if price <= 10:
                    distribution["Até R$ 10"] += 1
                elif price <= 20:
                    distribution["R$ 10-20"] += 1
                elif price <= 50:
                    distribution["R$ 20-50"] += 1
                elif price <= 100:
                    distribution["R$ 50-100"] += 1
                else:
                    distribution["Acima R$ 100"] += 1
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Erro na análise de preços: {e}")
            return {}
        finally:
            conn.close()
    
    def search_by_location(self, query: str, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Busca por localização (implementação básica)"""
        # TODO: Implementar busca geográfica real com coordenadas
        return self.search_restaurants(query=query)
    
    def get_recommendations(self, restaurant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recomenda restaurantes similares"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Pega categoria do restaurante base
            cursor.execute("SELECT categoria FROM restaurants WHERE id = ?", (restaurant_id,))
            base_restaurant = cursor.fetchone()
            
            if not base_restaurant:
                return []
            
            category = base_restaurant['categoria']
            
            # Busca restaurantes similares na mesma categoria
            sql = """
                SELECT * FROM restaurants 
                WHERE categoria = ? AND id != ?
                ORDER BY avaliacao DESC
                LIMIT ?
            """
            
            cursor.execute(sql, (category, restaurant_id, limit))
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {e}")
            return []
        finally:
            conn.close()
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Estatísticas básicas
            cursor.execute("SELECT COUNT(*) FROM restaurants")
            stats['total_restaurants'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT categoria) FROM restaurants WHERE categoria IS NOT NULL")
            stats['total_categories'] = cursor.fetchone()[0]
            
            # Estatísticas de preços
            cursor.execute("""
                SELECT 
                    AVG(preco_numerico) as avg_price,
                    MIN(preco_numerico) as min_price,
                    MAX(preco_numerico) as max_price,
                    COUNT(*) as products_with_price
                FROM products 
                WHERE preco_numerico > 0
            """)
            price_row = cursor.fetchone()
            if price_row:
                stats['price_stats'] = {
                    'avg_price': round(price_row[0], 2) if price_row[0] else 0,
                    'min_price': price_row[1] if price_row[1] else 0,
                    'max_price': price_row[2] if price_row[2] else 0,
                    'products_with_price': price_row[3] if price_row[3] else 0
                }
            
            # Estatísticas de avaliações
            cursor.execute("""
                SELECT 
                    AVG(CAST(avaliacao AS REAL)) as avg_rating,
                    MAX(CAST(avaliacao AS REAL)) as max_rating,
                    COUNT(*) as restaurants_with_rating
                FROM restaurants 
                WHERE avaliacao IS NOT NULL AND avaliacao != '' AND avaliacao != '0'
            """)
            rating_row = cursor.fetchone()
            if rating_row:
                stats['rating_stats'] = {
                    'avg_rating': round(rating_row[0], 2) if rating_row[0] else 0,
                    'max_rating': rating_row[1] if rating_row[1] else 0,
                    'restaurants_with_rating': rating_row[2] if rating_row[2] else 0
                }
            
            # Top categorias
            cursor.execute("""
                SELECT categoria, COUNT(*) as count
                FROM restaurants 
                WHERE categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria 
                ORDER BY count DESC
                LIMIT 10
            """)
            stats['top_categories'] = [
                {'categoria': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
        finally:
            conn.close()


def create_search_cli():
    """Interface de linha de comando para busca"""
    optimizer = QueryOptimizer()
    
    print("\n" + "="*60)
    print("SISTEMA DE BUSCA OTIMIZADA")
    print("="*60)
    
    while True:
        print("\nOpções:")
        print("1. Buscar restaurantes")
        print("2. Buscar produtos")
        print("3. Categorias populares")
        print("4. Análise de preços")
        print("5. Recomendações")
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
        
        elif choice == "0":
            break


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de busca otimizada")
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
        print("Sistema de Busca Otimizada")
        print("Use --help para ver opções disponíveis")
        
        # Executa setup básico
        index = SearchIndex()
        index.create_database_indexes()
        index.load_data_to_database()
        
        print("\nBanco criado e dados carregados!")
        print("Use --cli para interface de busca")