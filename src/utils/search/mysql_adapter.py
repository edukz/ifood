#!/usr/bin/env python3
"""
MySQL Adapter para Search System - Adapta o sistema de busca para usar MySQL ao invés de SQLite
"""

from typing import Dict, List, Any, Optional
from src.database.database_manager_v2 import get_database_manager
from src.utils.logger import setup_logger


class MySQLSearchAdapter:
    """Adaptador para usar MySQL com o sistema de busca"""
    
    def __init__(self):
        self.db = get_database_manager()
        self.logger = setup_logger("MySQLSearchAdapter")
    
    def get_popular_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna categorias mais populares por número de restaurantes"""
        try:
            sql = """
                SELECT c.name as categoria, COUNT(r.id) as restaurant_count,
                       AVG(r.rating) as avg_rating
                FROM categories c
                LEFT JOIN restaurants r ON c.id = r.category_id
                WHERE c.name IS NOT NULL AND c.name != ''
                GROUP BY c.id, c.name
                ORDER BY restaurant_count DESC, avg_rating DESC
                LIMIT %s
            """
            
            results = self.db.execute_query(sql, (limit,), fetch_all=True)
            
            if results:
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'categoria': row['categoria'],
                        'restaurant_count': row['restaurant_count'],
                        'avg_rating': round(row['avg_rating'], 2) if row['avg_rating'] else 0
                    })
                return formatted_results
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar categorias populares: {e}")
            return []
    
    def search_restaurants(self, 
                          query: str = None,
                          category: str = None,
                          min_rating: float = None,
                          city: str = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Busca restaurantes no MySQL"""
        try:
            sql = """
                SELECT r.id, r.name as nome, c.name as categoria, r.rating as avaliacao, 
                       r.delivery_time as tempo_entrega, r.delivery_fee as taxa_entrega,
                       r.distance as distancia, r.url, r.address as endereco, r.city
                FROM restaurants r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.is_active = TRUE
            """
            
            params = []
            
            if query:
                sql += " AND (r.name LIKE %s OR c.name LIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND c.name = %s"
                params.append(category)
            
            if min_rating is not None:
                sql += " AND r.rating >= %s"
                params.append(min_rating)
            
            if city:
                sql += " AND r.city = %s"
                params.append(city)
            
            sql += " ORDER BY r.rating DESC, r.name ASC LIMIT %s"
            params.append(limit)
            
            results = self.db.execute_query(sql, params, fetch_all=True)
            return results if results else []
            
        except Exception as e:
            self.logger.error(f"Erro na busca de restaurantes: {e}")
            return []
    
    def search_products(self,
                       query: str = None,
                       category: str = None,
                       min_price: float = None,
                       max_price: float = None,
                       restaurant_id: str = None,
                       available_only: bool = True,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Busca produtos no MySQL"""
        try:
            sql = """
                SELECT p.id, p.name as nome, p.description as descricao, p.price as preco,
                       p.original_price as preco_original, p.category as categoria_produto,
                       p.is_available as disponivel, p.image_url, p.restaurant_id,
                       r.name as restaurant_name
                FROM products p
                LEFT JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.is_active = TRUE
            """
            
            params = []
            
            if query:
                sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND p.category = %s"
                params.append(category)
            
            if min_price is not None:
                sql += " AND p.price >= %s"
                params.append(min_price)
            
            if max_price is not None:
                sql += " AND p.price <= %s"
                params.append(max_price)
            
            if restaurant_id:
                sql += " AND p.restaurant_id = %s"
                params.append(restaurant_id)
            
            if available_only:
                sql += " AND p.is_available = TRUE"
            
            sql += " ORDER BY p.price ASC, p.name ASC LIMIT %s"
            params.append(limit)
            
            results = self.db.execute_query(sql, params, fetch_all=True)
            return results if results else []
            
        except Exception as e:
            self.logger.error(f"Erro na busca de produtos: {e}")
            return []
    
    def get_price_distribution(self, category: str = None) -> Dict[str, int]:
        """Analisa distribuição de preços usando MySQL"""
        try:
            sql = "SELECT price FROM products WHERE price > 0 AND is_active = TRUE"
            params = []
            
            if category:
                sql += " AND category = %s"
                params.append(category)
            
            results = self.db.execute_query(sql, params, fetch_all=True)
            
            if not results:
                return {}
            
            prices = [float(row['price']) for row in results]
            
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
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco MySQL"""
        try:
            stats = {}
            
            # Estatísticas básicas
            restaurant_count = self.db.execute_query(
                "SELECT COUNT(*) as count FROM restaurants WHERE is_active = TRUE", 
                fetch_one=True
            )
            stats['total_restaurants'] = restaurant_count['count'] if restaurant_count else 0
            
            product_count = self.db.execute_query(
                "SELECT COUNT(*) as count FROM products WHERE is_active = TRUE", 
                fetch_one=True
            )
            stats['total_products'] = product_count['count'] if product_count else 0
            
            category_count = self.db.execute_query(
                "SELECT COUNT(*) as count FROM categories", 
                fetch_one=True
            )
            stats['total_categories'] = category_count['count'] if category_count else 0
            
            # Estatísticas de preços
            price_stats = self.db.execute_query("""
                SELECT 
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    COUNT(*) as products_with_price
                FROM products 
                WHERE price > 0 AND is_active = TRUE
            """, fetch_one=True)
            
            if price_stats:
                stats['price_stats'] = {
                    'avg_price': round(float(price_stats['avg_price']), 2) if price_stats['avg_price'] else 0,
                    'min_price': float(price_stats['min_price']) if price_stats['min_price'] else 0,
                    'max_price': float(price_stats['max_price']) if price_stats['max_price'] else 0,
                    'products_with_price': price_stats['products_with_price'] if price_stats['products_with_price'] else 0
                }
            
            # Estatísticas de avaliações
            rating_stats = self.db.execute_query("""
                SELECT 
                    AVG(rating) as avg_rating,
                    MAX(rating) as max_rating,
                    MIN(rating) as min_rating,
                    COUNT(*) as restaurants_with_rating
                FROM restaurants 
                WHERE rating IS NOT NULL AND rating > 0 AND is_active = TRUE
            """, fetch_one=True)
            
            if rating_stats:
                stats['rating_stats'] = {
                    'avg_rating': round(float(rating_stats['avg_rating']), 2) if rating_stats['avg_rating'] else 0,
                    'max_rating': float(rating_stats['max_rating']) if rating_stats['max_rating'] else 0,
                    'min_rating': float(rating_stats['min_rating']) if rating_stats['min_rating'] else 0,
                    'restaurants_with_rating': rating_stats['restaurants_with_rating'] if rating_stats['restaurants_with_rating'] else 0
                }
            
            # Top categorias
            top_categories = self.db.execute_query("""
                SELECT c.name as categoria, COUNT(r.id) as count, AVG(r.rating) as avg_rating
                FROM categories c
                LEFT JOIN restaurants r ON c.id = r.category_id AND r.is_active = TRUE
                WHERE c.name IS NOT NULL AND c.name != ''
                GROUP BY c.id, c.name
                ORDER BY count DESC
                LIMIT 10
            """, fetch_all=True)
            
            if top_categories:
                stats['top_categories'] = [
                    {
                        'categoria': row['categoria'],
                        'count': row['count'],
                        'avg_rating': round(float(row['avg_rating']), 2) if row['avg_rating'] else 0
                    }
                    for row in top_categories
                ]
            else:
                stats['top_categories'] = []
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def get_recommendations(self, restaurant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em um restaurante"""
        try:
            # Primeiro, obtém informações do restaurante base
            base_restaurant = self.db.execute_query("""
                SELECT r.category_id, r.rating, r.city
                FROM restaurants r
                WHERE r.id = %s AND r.is_active = TRUE
            """, (restaurant_id,), fetch_one=True)
            
            if not base_restaurant:
                return []
            
            # Busca restaurantes similares
            similar_restaurants = self.db.execute_query("""
                SELECT r.id, r.name as nome, c.name as categoria, r.rating as avaliacao, 
                       r.city, ABS(r.rating - %s) as rating_diff
                FROM restaurants r
                JOIN categories c ON r.category_id = c.id
                WHERE r.category_id = %s AND r.city = %s AND r.id != %s 
                      AND r.is_active = TRUE
                ORDER BY rating_diff ASC, r.rating DESC
                LIMIT %s
            """, (
                base_restaurant['rating'] or 0,
                base_restaurant['category_id'],
                base_restaurant['city'],
                restaurant_id,
                limit
            ), fetch_all=True)
            
            if similar_restaurants:
                # Remove o campo rating_diff dos resultados
                for result in similar_restaurants:
                    result.pop('rating_diff', None)
                
                return similar_restaurants
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {e}")
            return []