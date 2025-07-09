"""
Database Manager V2 - Sistema limpo e otimizado para MySQL
"""

import mysql.connector
from mysql.connector import pooling
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import hashlib
from contextlib import contextmanager
import os
from dotenv import load_dotenv

from src.utils.logger import setup_logger

# Carregar variáveis de ambiente
load_dotenv(override=True)  # Force reload

class DatabaseConfig:
    """Configuração do banco de dados"""
    def __init__(self):
        self.host = os.getenv('DB_HOST', '127.0.0.1')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'Dedolas1901*')
        self.database = os.getenv('DB_NAME', 'ifood_scraper_v3')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', 5))
        self.pool_name = "ifood_connection_pool"
        
        # Debug: mostrar qual configuração está sendo usada
        print(f"[DEBUG] Conectando com: {self.user}@{self.host}:{self.port}/{self.database}")
        
    def get_config(self) -> dict:
        """Retorna configuração para conexão"""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'use_unicode': True,
            'autocommit': False,
            'sql_mode': 'TRADITIONAL',
            'time_zone': '+00:00'
        }


class DatabaseManagerV2:
    """Gerenciador de banco de dados otimizado"""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.config = DatabaseConfig()
        self._connection_pool = None
        self._init_connection_pool()
        
    def _init_connection_pool(self):
        """Inicializa pool de conexões"""
        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name=self.config.pool_name,
                pool_size=self.config.pool_size,
                pool_reset_session=True,
                **self.config.get_config()
            )
            self.logger.info(f"Pool de conexões criado: {self.config.pool_size} conexões")
        except Exception as e:
            self.logger.error(f"Erro ao criar pool de conexões: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para obter conexão do pool"""
        connection = None
        try:
            connection = self._connection_pool.get_connection()
            yield connection
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager para obter cursor"""
        with self.get_connection() as connection:
            cursor = None
            try:
                cursor = connection.cursor(dictionary=dictionary)
                yield cursor, connection
                connection.commit()
            except Exception as e:
                if connection:
                    connection.rollback()
                self.logger.error(f"Erro na transação: {e}")
                raise
            finally:
                if cursor:
                    cursor.close()
    
    # ===== FUNÇÕES AUXILIARES =====
    
    @staticmethod
    def generate_unique_key(*args) -> str:
        """Gera chave única baseada em MD5"""
        # Limpar e normalizar strings
        parts = []
        for arg in args:
            if arg is not None:
                parts.append(str(arg).lower().strip())
        
        # Gerar hash
        combined = '|'.join(parts)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    @staticmethod
    def clean_price(price_str: str) -> float:
        """Converte string de preço para float"""
        if not price_str:
            return 0.0
        
        # Remove R$, espaços e converte vírgula para ponto
        clean = price_str.replace('R$', '').replace(' ', '').replace(',', '.')
        
        try:
            return float(clean)
        except:
            return 0.0
    
    # ===== OPERAÇÕES COM CATEGORIAS =====
    
    def save_categories(self, categories: List[Dict], city: str) -> Dict[str, int]:
        """Salva categorias no banco"""
        result = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        with self.get_cursor() as (cursor, connection):
            for category in categories:
                try:
                    # Preparar dados
                    slug = category.get('slug') or category['name'].lower().replace(' ', '-')
                    
                    # INSERT ... ON DUPLICATE KEY UPDATE
                    cursor.execute("""
                        INSERT INTO categories (name, slug, url, icon_url, city)
                        VALUES (%s, %s, %s, %s, %s) AS new_cat
                        ON DUPLICATE KEY UPDATE
                            name = new_cat.name,
                            url = new_cat.url,
                            icon_url = new_cat.icon_url,
                            city = new_cat.city,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        category['name'],
                        slug,
                        category.get('url', ''),
                        category.get('icon_url'),
                        city
                    ))
                    
                    if cursor.rowcount == 1:
                        result['inserted'] += 1
                    else:
                        result['updated'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao salvar categoria {category.get('name')}: {e}")
                    result['errors'] += 1
        
        self.logger.info(f"Categorias salvas - Inseridas: {result['inserted']}, "
                        f"Atualizadas: {result['updated']}, Erros: {result['errors']}")
        return result
    
    def get_category_id(self, category_name: str) -> Optional[int]:
        """Busca ID de uma categoria pelo nome"""
        with self.get_cursor() as (cursor, _):
            cursor.execute(
                "SELECT id FROM categories WHERE name = %s OR slug = %s LIMIT 1",
                (category_name, category_name.lower().replace(' ', '-'))
            )
            result = cursor.fetchone()
            return result['id'] if result else None
    
    # ===== OPERAÇÕES COM RESTAURANTES =====
    
    def save_restaurants(self, restaurants: List[Dict], category_name: str, city: str) -> Dict[str, int]:
        """Salva restaurantes no banco com prevenção de duplicatas"""
        result = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Buscar ID da categoria
        category_id = self.get_category_id(category_name)
        if not category_id:
            self.logger.error(f"Categoria '{category_name}' não encontrada!")
            return result
        
        with self.get_cursor() as (cursor, connection):
            for restaurant in restaurants:
                try:
                    # Gerar unique_key
                    unique_key = self.generate_unique_key(
                        restaurant['nome'],
                        category_name,
                        city
                    )
                    
                    # Preparar dados
                    rating = float(restaurant.get('avaliacao', 0) or 0)
                    
                    # INSERT ... ON DUPLICATE KEY UPDATE
                    cursor.execute("""
                        INSERT INTO restaurants (
                            unique_key, name, category_id, city, rating,
                            delivery_time, delivery_fee, distance, url, 
                            logo_url, address, phone, opening_hours, 
                            minimum_order, payment_methods, tags
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s
                        ) AS new_rest
                        ON DUPLICATE KEY UPDATE
                            rating = new_rest.rating,
                            delivery_time = new_rest.delivery_time,
                            delivery_fee = new_rest.delivery_fee,
                            distance = new_rest.distance,
                            logo_url = new_rest.logo_url,
                            address = COALESCE(new_rest.address, address),
                            phone = COALESCE(new_rest.phone, phone),
                            opening_hours = COALESCE(new_rest.opening_hours, opening_hours),
                            minimum_order = COALESCE(new_rest.minimum_order, minimum_order),
                            payment_methods = COALESCE(new_rest.payment_methods, payment_methods),
                            tags = COALESCE(new_rest.tags, tags),
                            last_scraped = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        unique_key,
                        restaurant['nome'],
                        category_id,
                        city,
                        rating,
                        restaurant.get('tempo_entrega'),
                        restaurant.get('taxa_entrega'),
                        restaurant.get('distancia'),
                        restaurant.get('url'),
                        restaurant.get('logo_url'),
                        restaurant.get('endereco'),
                        restaurant.get('telefone'),
                        restaurant.get('horario_funcionamento'),
                        restaurant.get('pedido_minimo'),
                        json.dumps(restaurant.get('formas_pagamento', [])),
                        json.dumps(restaurant.get('tags', []))
                    ))
                    
                    if cursor.rowcount == 1:
                        result['inserted'] += 1
                    else:
                        result['updated'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao salvar restaurante {restaurant.get('nome')}: {e}")
                    result['errors'] += 1
        
        self.logger.info(f"Restaurantes salvos - Inseridos: {result['inserted']}, "
                        f"Atualizados: {result['updated']}, Erros: {result['errors']}")
        return result
    
    def get_restaurant_id(self, restaurant_name: str, category_name: str, city: str) -> Optional[int]:
        """Busca ID de um restaurante"""
        unique_key = self.generate_unique_key(restaurant_name, category_name, city)
        
        with self.get_cursor() as (cursor, _):
            cursor.execute(
                "SELECT id FROM restaurants WHERE unique_key = %s LIMIT 1",
                (unique_key,)
            )
            result = cursor.fetchone()
            return result['id'] if result else None
    
    # ===== OPERAÇÕES COM PRODUTOS =====
    
    def save_products(self, products: List[Dict], restaurant_name: str, 
                     category_name: str, city: str) -> Dict[str, int]:
        """Salva produtos no banco com rastreamento de preços"""
        result = {'inserted': 0, 'updated': 0, 'price_changes': 0, 'errors': 0}
        
        # Buscar ID do restaurante
        restaurant_id = self.get_restaurant_id(restaurant_name, category_name, city)
        if not restaurant_id:
            self.logger.error(f"Restaurante '{restaurant_name}' não encontrado!")
            return result
        
        with self.get_cursor() as (cursor, connection):
            for product in products:
                try:
                    # Gerar unique_key
                    unique_key = self.generate_unique_key(
                        str(restaurant_id),
                        product['nome'],
                        product.get('categoria_produto', 'Geral')
                    )
                    
                    # Preparar dados
                    price = self.clean_price(product.get('preco', '0'))
                    original_price = self.clean_price(product.get('preco_original', '0'))
                    
                    # Verificar se produto existe e se preço mudou
                    cursor.execute("""
                        SELECT id, price FROM products 
                        WHERE unique_key = %s
                    """, (unique_key,))
                    
                    existing = cursor.fetchone()
                    
                    # Se preço mudou, registrar no histórico
                    if existing and existing['price'] != price:
                        cursor.execute("""
                            INSERT INTO price_history (product_id, price, original_price)
                            VALUES (%s, %s, %s)
                        """, (existing['id'], price, original_price or None))
                        result['price_changes'] += 1
                    
                    # INSERT ... ON DUPLICATE KEY UPDATE
                    cursor.execute("""
                        INSERT INTO products (
                            unique_key, restaurant_id, name, description,
                            category, price, original_price, image_url,
                            is_available, preparation_time, serves_people,
                            calories, ingredients, allergens
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) AS new_prod
                        ON DUPLICATE KEY UPDATE
                            description = new_prod.description,
                            price = new_prod.price,
                            original_price = new_prod.original_price,
                            image_url = new_prod.image_url,
                            is_available = new_prod.is_available,
                            preparation_time = new_prod.preparation_time,
                            serves_people = new_prod.serves_people,
                            calories = new_prod.calories,
                            ingredients = new_prod.ingredients,
                            allergens = new_prod.allergens,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        unique_key,
                        restaurant_id,
                        product['nome'],
                        product.get('descricao'),
                        product.get('categoria_produto', 'Geral'),
                        price,
                        original_price if original_price > 0 else None,
                        product.get('imagem_url'),
                        product.get('disponivel', True),
                        product.get('tempo_preparo'),
                        product.get('serve_pessoas'),
                        product.get('calorias'),
                        json.dumps(product.get('ingredientes', [])),
                        json.dumps(product.get('alergenos', []))
                    ))
                    
                    if cursor.rowcount == 1:
                        result['inserted'] += 1
                    else:
                        result['updated'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao salvar produto {product.get('nome')}: {e}")
                    result['errors'] += 1
        
        self.logger.info(f"Produtos salvos - Inseridos: {result['inserted']}, "
                        f"Atualizados: {result['updated']}, "
                        f"Mudanças de preço: {result['price_changes']}, "
                        f"Erros: {result['errors']}")
        return result
    
    # ===== OPERAÇÕES DE CONSULTA =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do banco"""
        stats = {}
        
        with self.get_cursor() as (cursor, _):
            # Total de categorias
            cursor.execute("SELECT COUNT(*) as total FROM categories")
            stats['categories'] = cursor.fetchone()['total']
            
            # Total de restaurantes
            cursor.execute("SELECT COUNT(*) as total FROM restaurants WHERE is_active = TRUE")
            stats['active_restaurants'] = cursor.fetchone()['total']
            
            # Total de produtos
            cursor.execute("SELECT COUNT(*) as total FROM products WHERE is_available = TRUE")
            stats['available_products'] = cursor.fetchone()['total']
            
            # Estatísticas por categoria
            cursor.execute("""
                SELECT c.name, COUNT(r.id) as count
                FROM categories c
                LEFT JOIN restaurants r ON c.id = r.category_id
                GROUP BY c.id, c.name
                ORDER BY count DESC
            """)
            stats['by_category'] = cursor.fetchall()
            
            # Mudanças de preço recentes
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM price_history 
                WHERE changed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            stats['recent_price_changes'] = cursor.fetchone()['total']
        
        return stats
    
    def search_restaurants(self, query: str, city: str = None, 
                          category: str = None, limit: int = 50) -> List[Dict]:
        """Busca restaurantes"""
        conditions = ["r.is_active = TRUE"]
        params = []
        
        if query:
            conditions.append("(r.name LIKE %s OR r.address LIKE %s)")
            params.extend([f'%{query}%', f'%{query}%'])
        
        if city:
            conditions.append("r.city = %s")
            params.append(city)
            
        if category:
            conditions.append("c.name = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        with self.get_cursor() as (cursor, _):
            cursor.execute(f"""
                SELECT r.*, c.name as category_name
                FROM restaurants r
                JOIN categories c ON r.category_id = c.id
                WHERE {where_clause}
                ORDER BY r.rating DESC
                LIMIT %s
            """, params + [limit])
            
            return cursor.fetchall()
    
    def search_products(self, query: str, min_price: float = None, 
                       max_price: float = None, limit: int = 50) -> List[Dict]:
        """Busca produtos"""
        conditions = ["p.is_available = TRUE"]
        params = []
        
        if query:
            conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
            params.extend([f'%{query}%', f'%{query}%'])
        
        if min_price is not None:
            conditions.append("p.price >= %s")
            params.append(min_price)
            
        if max_price is not None:
            conditions.append("p.price <= %s")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions)
        
        with self.get_cursor() as (cursor, _):
            cursor.execute(f"""
                SELECT p.*, r.name as restaurant_name, r.rating as restaurant_rating
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE {where_clause}
                ORDER BY r.rating DESC, p.price ASC
                LIMIT %s
            """, params + [limit])
            
            return cursor.fetchall()
    
    # ===== OPERAÇÕES DE MANUTENÇÃO =====
    
    def cleanup_duplicates(self) -> int:
        """Remove duplicatas mantendo o registro mais recente"""
        with self.get_cursor() as (cursor, connection):
            # Encontrar e remover duplicatas de restaurantes
            cursor.execute("""
                DELETE r1 FROM restaurants r1
                INNER JOIN restaurants r2 
                WHERE r1.id < r2.id 
                AND r1.unique_key = r2.unique_key
            """)
            
            deleted = cursor.rowcount
            self.logger.info(f"Removidas {deleted} duplicatas")
            return deleted
    
    def log_extraction(self, extraction_type: str, entity_name: str, 
                      status: str, items: int = 0, error: str = None) -> int:
        """Registra log de extração"""
        with self.get_cursor() as (cursor, connection):
            cursor.execute("""
                INSERT INTO extraction_logs 
                (extraction_type, entity_name, status, items_extracted, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (extraction_type, entity_name, status, items, error))
            
            return cursor.lastrowid
    
    def update_extraction_log(self, log_id: int, status: str, items: int = None, error: str = None):
        """Atualiza log de extração"""
        with self.get_cursor() as (cursor, connection):
            # Calcular duração
            cursor.execute("""
                UPDATE extraction_logs 
                SET status = %s,
                    items_extracted = COALESCE(%s, items_extracted),
                    error_message = %s,
                    completed_at = CURRENT_TIMESTAMP,
                    duration_seconds = TIMESTAMPDIFF(SECOND, started_at, CURRENT_TIMESTAMP)
                WHERE id = %s
            """, (status, items, error, log_id))
    
    def close(self):
        """Fecha o pool de conexões"""
        if self._connection_pool:
            self.logger.info("Fechando pool de conexões...")
            # Pool é fechado automaticamente


# Singleton para facilitar uso
_db_instance = None

def get_database_manager() -> DatabaseManagerV2:
    """Retorna instância única do gerenciador de banco"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManagerV2()
    return _db_instance