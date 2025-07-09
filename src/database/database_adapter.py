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
        try:
            self.db_v2 = get_db_v2()
            self.logger.info("Usando DatabaseManagerV2 através do adaptador")
            self._connected = True
        except Exception as e:
            self.logger.warning(f"MySQL não disponível: {e}")
            self.db_v2 = None
            self._connected = False
    
    # ===== MÉTODOS COMPATÍVEIS COM INTERFACE ANTIGA =====
    
    def save_categories(self, categories: List[Any], city: str) -> Dict[str, Any]:
        """Salva categorias (compatível com interface antiga)"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando resultado vazio")
            return {'new': 0, 'updated': 0, 'duplicates': 0, 'total': 0}
        
        try:
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
        except Exception as e:
            self.logger.error(f"Erro ao salvar categorias: {e}")
            return {'new': 0, 'updated': 0, 'duplicates': 0, 'total': 0}
    
    def save_restaurants(self, restaurants: List[Dict], category: str, city: str) -> Dict[str, Any]:
        """Salva restaurantes (compatível com interface antiga)"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando resultado vazio")
            return {'new': 0, 'duplicates': 0, 'total': 0, 'inserted': 0, 'updated': 0, 'error': 'MySQL não disponível'}
        
        try:
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
        except Exception as e:
            self.logger.error(f"Erro ao salvar restaurantes: {e}")
            return {'new': 0, 'duplicates': 0, 'total': 0, 'inserted': 0, 'updated': 0, 'error': str(e)}
    
    def save_products(self, products: List[Dict], restaurant_name: str, 
                     restaurant_id: str = None) -> Dict[str, Any]:
        """Salva produtos (compatível com interface antiga)"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando resultado vazio")
            return {'inserted': 0, 'updated': 0, 'price_changes': 0}
        
        try:
            # Precisamos descobrir categoria e cidade do restaurante
            # Por enquanto, vamos usar valores padrão
            # Em produção, seria melhor buscar essas informações
            
            # Tentar inferir categoria e cidade do contexto ou usar padrões
            from src.config.settings import SETTINGS
            category = 'Geral'  # Valor padrão
            city = SETTINGS.city  # Usar cidade das configurações
            
            result = self.db_v2.save_products(products, restaurant_name, category, city)
            
            return {
                'inserted': result['inserted'],
                'updated': result['updated'],
                'price_changes': result['price_changes']
            }
        except Exception as e:
            self.logger.error(f"Erro ao salvar produtos: {e}")
            return {'inserted': 0, 'updated': 0, 'price_changes': 0}
    
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
        if not self._connected or self.db_v2 is None:
            raise ConnectionError("MySQL não disponível")
        return self.db_v2.get_cursor(dictionary)
    
    # ===== MÉTODOS DE CONSULTA =====
    
    def get_categories(self, city: str = None) -> List[Dict]:
        """Busca categorias"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando lista vazia")
            return []
        
        try:
            with self.db_v2.get_cursor() as (cursor, _):
                if city:
                    cursor.execute(
                        "SELECT * FROM categories WHERE city = %s AND is_active = TRUE",
                        (city,)
                    )
                else:
                    cursor.execute("SELECT * FROM categories WHERE is_active = TRUE")
                
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Erro ao buscar categorias: {e}")
            return []
    
    def get_existing_categories(self, city: str = None) -> List[Dict]:
        """Busca categorias existentes (alias para get_categories)"""
        return self.get_categories(city)
    
    def get_restaurants(self, city: str = None, limit: int = None) -> List[Dict]:
        """Busca todos os restaurantes"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando lista vazia")
            return []
        try:
            with self.db_v2.get_cursor() as (cursor, _):
                if city:
                    query = "SELECT * FROM restaurants WHERE city = %s AND is_active = TRUE ORDER BY rating DESC"
                    params = (city,)
                else:
                    query = "SELECT * FROM restaurants WHERE is_active = TRUE ORDER BY rating DESC"
                    params = ()
                
                if limit:
                    query += " LIMIT %s"
                    params = params + (limit,)
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Erro ao buscar restaurantes: {e}")
            return []
    
    def get_restaurants_by_category(self, category: str, city: str = None, limit: int = None) -> List[Dict]:
        """Busca restaurantes por categoria"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando lista vazia")
            return []
        
        try:
            with self.db_v2.get_cursor() as (cursor, _):
                query = """
                    SELECT r.* FROM restaurants r
                    JOIN categories c ON r.category_id = c.id
                    WHERE c.slug = %s AND r.is_active = TRUE
                """
                params = [category]
                
                if city:
                    query += " AND r.city = %s"
                    params.append(city)
                
                query += " ORDER BY r.rating DESC"
                
                if limit:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Erro ao buscar restaurantes por categoria: {e}")
            return []
    
    def count_restaurants(self, city: str = None) -> int:
        """Conta total de restaurantes"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando 0")
            return 0
        
        try:
            with self.db_v2.get_cursor() as (cursor, _):
                if city:
                    cursor.execute(
                        "SELECT COUNT(*) as total FROM restaurants WHERE city = %s AND is_active = TRUE",
                        (city,)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) as total FROM restaurants WHERE is_active = TRUE")
                
                result = cursor.fetchone()
                return result['total'] if result else 0
        except Exception as e:
            self.logger.error(f"Erro ao contar restaurantes: {e}")
            return 0
    
    def get_products_by_restaurant(self, restaurant_name: str) -> List[Dict]:
        """Busca produtos de um restaurante"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando lista vazia")
            return []
        
        try:
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
        except Exception as e:
            self.logger.error(f"Erro ao buscar produtos do restaurante: {e}")
            return []
    
    # ===== ESTATÍSTICAS =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas (compatível)"""
        if not self._connected or self.db_v2 is None:
            self.logger.warning("MySQL não disponível - retornando estatísticas vazias")
            return {
                'total_categories': 0,
                'total_restaurants': 0,
                'total_products': 0,
                'categories': {},
                'price_changes_7d': 0
            }
        
        try:
            stats = self.db_v2.get_statistics()
            
            # Adaptar para formato antigo se necessário
            return {
                'total_categories': stats['categories'],
                'total_restaurants': stats['active_restaurants'],
                'total_products': stats['available_products'],
                'categories': stats['by_category'],
                'price_changes_7d': stats['recent_price_changes']
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_categories': 0,
                'total_restaurants': 0,
                'total_products': 0,
                'categories': {},
                'price_changes_7d': 0
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
        if self._connected and self.db_v2 is not None:
            try:
                self.db_v2.close()
            except Exception as e:
                self.logger.error(f"Erro ao fechar conexão: {e}")


# ===== FUNÇÕES DE COMPATIBILIDADE =====

def get_database_manager():
    """Retorna instância do adaptador (mantém assinatura antiga)"""
    return DatabaseAdapter()


# Alias para manter compatibilidade
MonitoredDatabaseManager = DatabaseAdapter
DatabaseManager = DatabaseAdapter