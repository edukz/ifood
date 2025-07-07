"""
Configuração de Conexão com MySQL
Substitui o SQLite por MySQL como banco principal
"""

import mysql.connector
from mysql.connector import pooling
import os
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

# Importa sistema de retry
from src.utils.retry_handler import (
    mysql_retry_manager, RetryConfig, retry_connection, retry_operation
)

logger = logging.getLogger(__name__)

class MySQLConfig:
    """Configuração centralized do MySQL"""
    
    # Configurações padrão
    DEFAULT_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'ifood',
        'password': None,  # Deve ser definido via variável de ambiente
        'database': 'ifood_scraper',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False,
        'raise_on_warnings': True,
        'time_zone': '-03:00'  # Horário de Brasília
    }
    
    # Pool de conexões
    POOL_CONFIG = {
        'pool_name': 'ifood_pool',
        'pool_size': 10,
        'pool_reset_session': True,
        'autocommit': False
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Retorna configuração com variáveis de ambiente"""
        config = cls.DEFAULT_CONFIG.copy()
        
        # Sobrescrever com variáveis de ambiente se existirem
        env_mapping = {
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_USER': 'user',
            'DB_PASSWORD': 'password',
            'DB_NAME': 'database'
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                # Converter port para int
                if config_key == 'port':
                    value = int(value)
                config[config_key] = value
        
        # Verificar se a senha foi definida
        if not config.get('password'):
            raise ValueError(
                "DB_PASSWORD não foi definida! "
                "Por favor, configure a variável de ambiente DB_PASSWORD ou "
                "crie um arquivo .env baseado no .env.example"
            )
        
        return config


class DatabaseManager:
    """Gerenciador de conexões MySQL com pool"""
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialize_pool()
            self._initialized = True
    
    @retry_connection
    def _initialize_pool(self):
        """Inicializa o pool de conexões com retry"""
        try:
            config = MySQLConfig.get_config()
            pool_config = MySQLConfig.POOL_CONFIG.copy()
            pool_config.update(config)
            
            self._pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"✅ Pool MySQL inicializado: {config['database']}@{config['host']}")
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Erro ao inicializar pool MySQL: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões do pool com retry"""
        connection = None
        try:
            # Aplica retry apenas na obtenção da conexão
            connection = self._get_pooled_connection()
            yield connection
        except mysql.connector.Error as e:
            logger.error(f"❌ Erro na conexão MySQL: {e}")
            if connection:
                try:
                    connection.rollback()
                except:
                    pass  # Ignora erros no rollback se conexão já morreu
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @retry_connection
    def _get_pooled_connection(self):
        """Obtém conexão do pool com retry"""
        return self._pool.get_connection()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager para cursor com auto-commit/rollback"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor, connection
                connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error(f"❌ Erro no cursor, rollback executado: {e}")
                raise
            finally:
                cursor.close()
    
    @retry_operation
    def execute_query(self, query: str, params: Optional[tuple] = None, 
                     fetch_one: bool = False, fetch_all: bool = True) -> Any:
        """Executa query simples com retorno de dados e retry"""
        with self.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.rowcount
    
    @retry_operation
    def execute_many(self, query: str, params_list: list) -> int:
        """Executa múltiplas queries com mesma estrutura e retry"""
        with self.get_cursor() as (cursor, connection):
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def test_connection(self) -> bool:
        """Testa conexão com o banco"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result[0] == 1
        except Exception as e:
            logger.error(f"❌ Teste de conexão falhou: {e}")
            return False


# Instância global do gerenciador
db_manager = DatabaseManager()

# Funções de conveniência para compatibilidade
def get_connection():
    """Retorna context manager de conexão"""
    return db_manager.get_connection()

def get_cursor(dictionary=True):
    """Retorna context manager de cursor"""
    return db_manager.get_cursor(dictionary=dictionary)

def execute_query(query: str, params: Optional[tuple] = None, 
                 fetch_one: bool = False, fetch_all: bool = True) -> Any:
    """Executa query simples"""
    return db_manager.execute_query(query, params, fetch_one, fetch_all)

def execute_many(query: str, params_list: list) -> int:
    """Executa múltiplas queries"""
    return db_manager.execute_many(query, params_list)

def test_connection() -> bool:
    """Testa conexão"""
    return db_manager.test_connection()


# Queries SQL comuns
class CommonQueries:
    """Queries SQL frequentemente utilizadas"""
    
    # Categorias
    GET_CATEGORIES = "SELECT * FROM categories WHERE is_active = TRUE ORDER BY name"
    GET_CATEGORY_BY_SLUG = "SELECT * FROM categories WHERE slug = %s"
    INSERT_CATEGORY = """
        INSERT INTO categories (name, slug, url, icon_url) 
        VALUES (%s, %s, %s, %s) AS new_values
        ON DUPLICATE KEY UPDATE name = new_values.name, url = new_values.url
    """
    
    # Restaurantes
    GET_RESTAURANTS_BY_CATEGORY = """
        SELECT * FROM restaurants 
        WHERE category_id = %s AND is_active = TRUE 
        ORDER BY rating DESC, name
    """
    GET_RESTAURANT_BY_NAME = "SELECT * FROM restaurants WHERE name = %s"
    INSERT_RESTAURANT = """
        INSERT INTO restaurants 
        (name, category_id, category_name, rating, delivery_time, delivery_fee, 
         distance, url, address, phone, opening_hours, minimum_order, promotions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Produtos
    GET_PRODUCTS_BY_RESTAURANT = """
        SELECT * FROM products 
        WHERE restaurant_id = %s AND is_available = TRUE 
        ORDER BY product_category, name
    """
    GET_PRODUCT_BY_HASH = "SELECT * FROM products WHERE hash_key = %s"
    INSERT_PRODUCT = """
        INSERT INTO products 
        (restaurant_id, name, description, price, original_price, product_category,
         is_available, image_url, preparation_time, serves_people, calories, 
         tags, ingredients, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Estatísticas
    COUNT_RESTAURANTS = "SELECT COUNT(*) FROM restaurants WHERE is_active = TRUE"
    COUNT_PRODUCTS = "SELECT COUNT(*) FROM products WHERE is_available = TRUE"
    COUNT_CATEGORIES = "SELECT COUNT(*) FROM categories WHERE is_active = TRUE"
    
    # Busca
    SEARCH_PRODUCTS = """
        SELECT p.*, r.name as restaurant_name, r.rating as restaurant_rating
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE MATCH(p.name, p.description) AGAINST(%s IN NATURAL LANGUAGE MODE)
        AND p.is_available = TRUE AND r.is_active = TRUE
        ORDER BY r.rating DESC
        LIMIT %s
    """


def get_retry_status() -> dict:
    """Retorna status do sistema de retry"""
    return mysql_retry_manager.get_status()


def reset_circuit_breakers():
    """Reseta circuit breakers manualmente"""
    if mysql_retry_manager.connection_breaker:
        mysql_retry_manager.connection_breaker.state = 'closed'
        mysql_retry_manager.connection_breaker.failure_count = 0
    
    if mysql_retry_manager.operation_breaker:
        mysql_retry_manager.operation_breaker.state = 'closed'
        mysql_retry_manager.operation_breaker.failure_count = 0
    
    logger.info("🔄 Circuit breakers resetados")


if __name__ == "__main__":
    # Teste da configuração com retry
    print("🔍 Testando configuração MySQL com retry...")
    
    try:
        if test_connection():
            print("✅ Conexão MySQL funcionando!")
            
            # Mostrar estatísticas
            stats = {
                'categories': execute_query(CommonQueries.COUNT_CATEGORIES, fetch_one=True),
                'restaurants': execute_query(CommonQueries.COUNT_RESTAURANTS, fetch_one=True),
                'products': execute_query(CommonQueries.COUNT_PRODUCTS, fetch_one=True)
            }
            
            print("\n📊 Estatísticas do banco:")
            for table, count in stats.items():
                print(f"   • {table.capitalize()}: {count[0] if count else 0:,}")
            
            # Status do sistema de retry
            retry_status = get_retry_status()
            print(f"\n🔄 Status do sistema de retry:")
            for breaker_name, status in retry_status.items():
                print(f"   • {breaker_name}: {status['state']} (falhas: {status['failure_count']})")
                
        else:
            print("❌ Falha na conexão MySQL")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"🔄 Status retry: {get_retry_status()}")