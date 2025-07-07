"""
Adaptador para fazer os scrapers existentes funcionarem com o novo DatabaseManagerV2
Mantém compatibilidade com a interface antiga
"""

from typing import List, Dict, Any, Optional
import json
from src.database.database_manager_v2 import get_database_manager as get_db_v2
from src.utils.logger import setup_logger


class DatabaseAdapter:
    """Adaptador que mantém compatibilidade com código existente"""
    
    def __init__(self):
        self.logger = setup_logger("DatabaseAdapter")
        self.db_v2 = get_db_v2()
        self.logger.info("Usando DatabaseManagerV2 através do adaptador")
    
    # ===== MÉTODOS COMPATÍVEIS COM INTERFACE ANTIGA =====
    
    def save_categories(self, categories: List[Any], city: str) -> Dict[str, Any]:
        """Salva categorias (compatível com interface antiga)"""
        # Converter formato antigo para novo se necessário
        formatted_categories = []
        
        for cat in categories:
            if hasattr(cat, '__dict__'):  # Se for objeto
                formatted_categories.append({
                    'name': cat.name,
                    'slug': getattr(cat, 'slug', None),
                    'url': cat.url,
                    'icon_url': getattr(cat, 'icon_url', None)
                })
            else:  # Se já for dict
                formatted_categories.append(cat)
        
        result = self.db_v2.save_categories(formatted_categories, city)
        
        # Adaptar resultado para formato esperado
        return {
            'new': result['inserted'],
            'updated': result['updated'],
            'duplicates': 0,
            'total': result['inserted'] + result['updated']
        }
    
    def save_restaurants(self, restaurants: List[Dict], category: str, city: str) -> Dict[str, Any]:
        """Salva restaurantes (compatível com interface antiga)"""
        result = self.db_v2.save_restaurants(restaurants, category, city)
        
        # Adaptar resultado para formato esperado pelo RestaurantScraper
        return {
            'new': result['inserted'],
            'duplicates': result['updated'],
            'total': result['inserted'] + result['updated'],
            'inserted': result['inserted'],
            'updated': result['updated'],
            'error': None if result['errors'] == 0 else f"{result['errors']} erros"
        }
    
    def save_products(self, products: List[Dict], restaurant_name: str, 
                     restaurant_id: str = None) -> Dict[str, Any]:
        """Salva produtos (compatível com interface antiga)"""
        # Precisamos descobrir categoria e cidade do restaurante
        # Por enquanto, vamos usar valores padrão
        # Em produção, seria melhor buscar essas informações
        
        # Tentar inferir categoria e cidade do contexto ou usar padrões
        category = 'Geral'  # Valor padrão
        city = 'São Paulo'  # Valor padrão
        
        result = self.db_v2.save_products(products, restaurant_name, category, city)
        
        return {
            'inserted': result['inserted'],
            'updated': result['updated'],
            'price_changes': result['price_changes']
        }
    
    def save_restaurants_monitored(self, restaurants: List[Dict], category: str, city: str) -> Dict[str, Any]:
        """Versão monitorada (redireciona para save_restaurants)"""
        return self.save_restaurants(restaurants, category, city)
    
    def save_products_monitored(self, products: List[Dict], restaurant_name: str, 
                               restaurant_id: str = None) -> Dict[str, Any]:
        """Versão monitorada (redireciona para save_products)"""
        return self.save_products(products, restaurant_name, restaurant_id)
    
    # ===== MÉTODOS DE ACESSO AO BANCO =====
    
    def get_cursor(self, dictionary=True):
        """Retorna cursor do banco (compatibilidade)"""
        return self.db_v2.get_cursor(dictionary)
    
    # ===== MÉTODOS DE CONSULTA =====
    
    def get_categories(self, city: str = None) -> List[Dict]:
        """Busca categorias"""
        with self.db_v2.get_cursor() as (cursor, _):
            if city:
                cursor.execute(
                    "SELECT * FROM categories WHERE city = %s AND is_active = TRUE",
                    (city,)
                )
            else:
                cursor.execute("SELECT * FROM categories WHERE is_active = TRUE")
            
            return cursor.fetchall()
    
    def get_existing_categories(self, city: str = None) -> List[Dict]:
        """Busca categorias existentes (alias para get_categories)"""
        return self.get_categories(city)
    
    def get_restaurants_by_category(self, category: str, city: str = None) -> List[Dict]:
        """Busca restaurantes por categoria"""
        return self.db_v2.search_restaurants('', city=city, category=category)
    
    def get_products_by_restaurant(self, restaurant_name: str) -> List[Dict]:
        """Busca produtos de um restaurante"""
        # Primeiro buscar o restaurante
        restaurants = self.db_v2.search_restaurants(restaurant_name, limit=1)
        if not restaurants:
            return []
        
        restaurant_id = restaurants[0]['id']
        
        with self.db_v2.get_cursor() as (cursor, _):
            cursor.execute("""
                SELECT * FROM products 
                WHERE restaurant_id = %s AND is_available = TRUE
                ORDER BY category, name
            """, (restaurant_id,))
            
            return cursor.fetchall()
    
    # ===== ESTATÍSTICAS =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas (compatível)"""
        stats = self.db_v2.get_statistics()
        
        # Adaptar para formato antigo se necessário
        return {
            'total_categories': stats['categories'],
            'total_restaurants': stats['active_restaurants'],
            'total_products': stats['available_products'],
            'categories': stats['by_category'],
            'price_changes_7d': stats['recent_price_changes']
        }
    
    def check_categories_status(self) -> Dict[str, Any]:
        """Verifica status das categorias"""
        return self.get_statistics()
    
    # ===== CACHE (SIMULADO) =====
    
    def _refresh_category_cache(self):
        """Simula refresh de cache (não necessário no V2)"""
        self.logger.debug("Cache refresh chamado (não necessário no V2)")
    
    def _refresh_restaurant_cache(self):
        """Simula refresh de cache (não necessário no V2)"""
        self.logger.debug("Cache refresh chamado (não necessário no V2)")
    
    # ===== COMPATIBILIDADE COM ATRIBUTOS =====
    
    @property
    def local_stats(self):
        """Simula estatísticas locais"""
        return {
            'operations_completed': 0,
            'total_items_processed': 0,
            'errors_encountered': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    @property
    def performance_monitor(self):
        """Simula monitor de performance"""
        return None
    
    def close(self):
        """Fecha conexões"""
        self.db_v2.close()


# ===== FUNÇÕES DE COMPATIBILIDADE =====

def get_database_manager():
    """Retorna instância do adaptador (mantém assinatura antiga)"""
    return DatabaseAdapter()


# Alias para manter compatibilidade
MonitoredDatabaseManager = DatabaseAdapter
DatabaseManager = DatabaseAdapter