#!/usr/bin/env python3
"""
Search Query Engine - Motor de execução de consultas e buscas otimizadas
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

from src.utils.logger import setup_logger


class SearchQueryEngine:
    """Motor de execução de consultas para buscas otimizadas"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.db_path = self.index_dir / "search_database.db"
        self.logger = setup_logger("SearchQueryEngine")
    
    def search_restaurants(self, 
                          query: str = None,
                          category: str = None,
                          min_rating: float = None,
                          max_delivery_fee: str = None,
                          city: str = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Busca otimizada de restaurantes com múltiplos filtros"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        try:
            # Constrói query SQL otimizada
            sql = "SELECT * FROM restaurants WHERE 1=1"
            params = []
            
            # Filtro por texto (nome ou categoria)
            if query:
                sql += " AND (nome LIKE ? OR categoria LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            # Filtro por categoria específica
            if category:
                sql += " AND categoria = ?"
                params.append(category)
            
            # Filtro por avaliação mínima
            if min_rating is not None:
                sql += " AND avaliacao >= ?"
                params.append(min_rating)
            
            # Filtro por cidade
            if city:
                sql += " AND city = ?"
                params.append(city)
            
            # Filtro por taxa de entrega máxima
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
        """Busca otimizada de produtos com filtros avançados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            sql = "SELECT * FROM products WHERE 1=1"
            params = []
            
            # Filtro por texto (nome ou descrição)
            if query:
                sql += " AND (nome LIKE ? OR descricao LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            # Filtro por categoria de produto
            if category:
                sql += " AND categoria_produto = ?"
                params.append(category)
            
            # Filtro por preço mínimo
            if min_price is not None:
                sql += " AND preco_numerico >= ?"
                params.append(min_price)
            
            # Filtro por preço máximo
            if max_price is not None:
                sql += " AND preco_numerico <= ?"
                params.append(max_price)
            
            # Filtro por restaurante específico
            if restaurant_id:
                sql += " AND restaurant_id = ?"
                params.append(restaurant_id)
            
            # Filtro apenas produtos disponíveis
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
    
    def search_by_location(self, city: str, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca restaurantes por localização"""
        return self.search_restaurants(
            city=city,
            category=category,
            limit=limit
        )
    
    def search_by_price_range(self, min_price: float, max_price: float, 
                             category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Busca produtos por faixa de preço"""
        return self.search_products(
            min_price=min_price,
            max_price=max_price,
            category=category,
            limit=limit
        )
    
    def get_recommendations(self, restaurant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas em um restaurante"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Primeiro, obtém informações do restaurante base
            cursor.execute("SELECT categoria, avaliacao, city FROM restaurants WHERE id = ?", (restaurant_id,))
            base_restaurant = cursor.fetchone()
            
            if not base_restaurant:
                return []
            
            # Busca restaurantes similares (mesma categoria e cidade, avaliação próxima)
            sql = """
                SELECT *, ABS(avaliacao - ?) as rating_diff 
                FROM restaurants 
                WHERE categoria = ? AND city = ? AND id != ?
                ORDER BY rating_diff ASC, avaliacao DESC
                LIMIT ?
            """
            
            cursor.execute(sql, (
                base_restaurant['avaliacao'] or 0,
                base_restaurant['categoria'],
                base_restaurant['city'],
                restaurant_id,
                limit
            ))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Remove o campo rating_diff dos resultados
            for result in results:
                result.pop('rating_diff', None)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {e}")
            return []
        finally:
            conn.close()
    
    def advanced_search(self, filters: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Busca avançada com múltiplos critérios"""
        results = {
            'restaurants': [],
            'products': []
        }
        
        try:
            # Filtros para restaurantes
            restaurant_filters = {
                'query': filters.get('query'),
                'category': filters.get('restaurant_category'),
                'min_rating': filters.get('min_rating'),
                'city': filters.get('city'),
                'limit': filters.get('restaurant_limit', 50)
            }
            
            # Remove filtros None
            restaurant_filters = {k: v for k, v in restaurant_filters.items() if v is not None}
            results['restaurants'] = self.search_restaurants(**restaurant_filters)
            
            # Filtros para produtos
            product_filters = {
                'query': filters.get('query'),
                'category': filters.get('product_category'),
                'min_price': filters.get('min_price'),
                'max_price': filters.get('max_price'),
                'available_only': filters.get('available_only', True),
                'limit': filters.get('product_limit', 100)
            }
            
            # Remove filtros None
            product_filters = {k: v for k, v in product_filters.items() if v is not None}
            results['products'] = self.search_products(**product_filters)
            
        except Exception as e:
            self.logger.error(f"Erro na busca avançada: {e}")
        
        return results
    
    def search_with_fuzzy_matching(self, query: str, table: str = 'restaurants', 
                                  limit: int = 20) -> List[Dict[str, Any]]:
        """Busca com correspondência aproximada para lidar com erros de digitação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Normaliza a query removendo acentos e caracteres especiais
            normalized_query = re.sub(r'[^\w\s]', '', query.lower())
            query_words = normalized_query.split()
            
            if table == 'restaurants':
                # Busca em restaurantes com correspondência parcial
                sql = "SELECT * FROM restaurants WHERE "
                conditions = []
                params = []
                
                for word in query_words:
                    conditions.append("(LOWER(nome) LIKE ? OR LOWER(categoria) LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%"])
                
                sql += " OR ".join(conditions)
                sql += " ORDER BY avaliacao DESC LIMIT ?"
                params.append(limit)
                
            else:  # products
                sql = "SELECT * FROM products WHERE "
                conditions = []
                params = []
                
                for word in query_words:
                    conditions.append("(LOWER(nome) LIKE ? OR LOWER(descricao) LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%"])
                
                sql += " OR ".join(conditions)
                sql += " ORDER BY preco_numerico ASC LIMIT ?"
                params.append(limit)
            
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca fuzzy: {e}")
            return []
        finally:
            conn.close()
    
    def get_trending_items(self, table: str = 'restaurants', limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna itens em tendência (mais bem avaliados recentemente)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if table == 'restaurants':
                sql = """
                    SELECT * FROM restaurants 
                    WHERE avaliacao IS NOT NULL 
                    ORDER BY avaliacao DESC, extracted_at DESC 
                    LIMIT ?
                """
            else:  # products
                sql = """
                    SELECT * FROM products 
                    WHERE disponivel = 1 AND preco_numerico > 0
                    ORDER BY extracted_at DESC, preco_numerico ASC 
                    LIMIT ?
                """
            
            cursor.execute(sql, (limit,))
            results = [dict(row) for row in cursor.fetchall()]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar itens em tendência: {e}")
            return []
        finally:
            conn.close()