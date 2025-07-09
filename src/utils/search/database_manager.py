#!/usr/bin/env python3
"""
Search Database Manager - Gerenciamento de banco de dados e índices para busca otimizada
"""

import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


class SearchDatabaseManager:
    """Gerenciador de banco de dados e índices para busca otimizada"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger("SearchDatabaseManager")
        
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
    
    def get_database_path(self) -> Path:
        """Retorna o caminho do banco de dados"""
        return self.index_dir / "search_database.db"
    
    def create_database_indexes(self):
        """Cria banco SQLite com índices otimizados"""
        db_path = self.get_database_path()
        
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
            
            # Criar índices para busca rápida
            self._create_database_indexes(cursor)
            
            conn.commit()
            self.logger.info("Banco de dados com índices criado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar banco de dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _create_database_indexes(self, cursor):
        """Cria índices otimizados no banco de dados"""
        indexes = [
            # Índices simples para restaurantes
            "CREATE INDEX IF NOT EXISTS idx_restaurants_nome ON restaurants (nome)",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_categoria ON restaurants (categoria)",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_avaliacao ON restaurants (avaliacao)",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants (city)",
            
            # Índices simples para produtos
            "CREATE INDEX IF NOT EXISTS idx_products_nome ON products (nome)",
            "CREATE INDEX IF NOT EXISTS idx_products_preco ON products (preco_numerico)",
            "CREATE INDEX IF NOT EXISTS idx_products_categoria ON products (categoria_produto)",
            "CREATE INDEX IF NOT EXISTS idx_products_restaurant ON products (restaurant_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_disponivel ON products (disponivel)",
            
            # Índices simples para categorias
            "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name)",
            "CREATE INDEX IF NOT EXISTS idx_categories_city ON categories (city)",
            
            # Índices compostos para consultas complexas
            "CREATE INDEX IF NOT EXISTS idx_restaurants_categoria_avaliacao ON restaurants (categoria, avaliacao DESC)",
            "CREATE INDEX IF NOT EXISTS idx_products_categoria_preco ON products (categoria_produto, preco_numerico)",
            "CREATE INDEX IF NOT EXISTS idx_products_restaurant_categoria ON products (restaurant_id, categoria_produto)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def load_data_to_database(self, data_dir: Path = None):
        """Carrega dados CSV para o banco SQLite"""
        data_dir = data_dir or Path(SETTINGS.output_dir)
        db_path = self.get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Limpa dados existentes
            self._clear_database_tables(cursor)
            
            # Carrega dados por tipo
            self._load_categories_data(data_dir, cursor)
            self._load_restaurants_data(data_dir, cursor)
            self._load_products_data(data_dir, cursor)
            
            conn.commit()
            
            # Atualiza estatísticas
            self._update_database_stats(cursor)
            
            self.logger.info("Dados carregados no banco com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _clear_database_tables(self, cursor):
        """Limpa todas as tabelas do banco"""
        cursor.execute("DELETE FROM restaurants")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
    
    def _load_categories_data(self, data_dir: Path, cursor):
        """Carrega dados de categorias"""
        categories_dir = data_dir / "categories"
        if categories_dir.exists():
            for csv_file in categories_dir.glob("*.csv"):
                self._load_csv_to_table(csv_file, "categories", cursor)
    
    def _load_restaurants_data(self, data_dir: Path, cursor):
        """Carrega dados de restaurantes"""
        restaurants_dir = data_dir / "restaurants"
        if restaurants_dir.exists():
            for csv_file in restaurants_dir.glob("*.csv"):
                self._load_csv_to_table(csv_file, "restaurants", cursor)
    
    def _load_products_data(self, data_dir: Path, cursor):
        """Carrega dados de produtos"""
        products_dir = data_dir / "products"
        if products_dir.exists():
            for csv_file in products_dir.glob("*.csv"):
                self._load_csv_to_table(csv_file, "products", cursor)
    
    def _load_csv_to_table(self, csv_file: Path, table_name: str, cursor):
        """Carrega um arquivo CSV específico para uma tabela"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if table_name == "products":
                        # Converte preço para número para busca numérica
                        row['preco_numerico'] = self._convert_price_to_numeric(row.get('preco', ''))
                    
                    # Insere dados baseado na tabela
                    self._insert_row_to_table(table_name, row, cursor)
        
        except Exception as e:
            self.logger.error(f"Erro ao carregar {csv_file}: {e}")
    
    def _convert_price_to_numeric(self, preco_str: str) -> float:
        """Converte string de preço para número"""
        try:
            preco_clean = preco_str.replace('R$', '').replace(' ', '').replace(',', '.')
            return float(preco_clean) if preco_clean and preco_clean != 'Não informado' else 0
        except (ValueError, AttributeError):
            return 0
    
    def _insert_row_to_table(self, table_name: str, row: Dict[str, Any], cursor):
        """Insere uma linha na tabela específica"""
        if table_name == "restaurants":
            self._insert_restaurant_row(row, cursor)
        elif table_name == "products":
            self._insert_product_row(row, cursor)
        elif table_name == "categories":
            self._insert_category_row(row, cursor)
    
    def _insert_restaurant_row(self, row: Dict[str, Any], cursor):
        """Insere dados de restaurante"""
        placeholders = ",".join(["?" for _ in range(11)])
        cursor.execute(f"""
            INSERT OR REPLACE INTO restaurants 
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
    
    def _insert_product_row(self, row: Dict[str, Any], cursor):
        """Insere dados de produto"""
        placeholders = ",".join(["?" for _ in range(16)])
        cursor.execute(f"""
            INSERT OR REPLACE INTO products
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
    
    def _insert_category_row(self, row: Dict[str, Any], cursor):
        """Insere dados de categoria"""
        placeholders = ",".join(["?" for _ in range(7)])
        cursor.execute(f"""
            INSERT OR REPLACE INTO categories
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
            
            # Atualiza metadados
            self.index_metadata.update({
                'total_records': restaurants_count + products_count + categories_count,
                'last_updated': str(datetime.now())
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        db_path = self.get_database_path()
        
        if not db_path.exists():
            return {
                'total_restaurants': 0,
                'total_products': 0,
                'total_categories': 0,
                'database_exists': False
            }
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM restaurants")
            restaurants_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            products_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM categories")
            categories_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_restaurants': restaurants_count,
                'total_products': products_count,
                'total_categories': categories_count,
                'database_exists': True,
                'metadata': self.index_metadata
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_restaurants': 0,
                'total_products': 0,
                'total_categories': 0,
                'database_exists': False,
                'error': str(e)
            }