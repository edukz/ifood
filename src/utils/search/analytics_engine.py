#!/usr/bin/env python3
"""
Search Analytics Engine - Motor de análise de dados e geração de insights
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.logger import setup_logger


class SearchAnalyticsEngine:
    """Motor de análise de dados e geração de insights"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path("cache/search_indexes")
        self.db_path = self.index_dir / "search_database.db"
        self.logger = setup_logger("SearchAnalyticsEngine")
    
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
        """Analisa distribuição de preços por faixas"""
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
            stats['price_stats'] = self._get_price_statistics(cursor)
            
            # Estatísticas de avaliações
            stats['rating_stats'] = self._get_rating_statistics(cursor)
            
            # Top categorias
            stats['top_categories'] = self._get_top_categories(cursor)
            
            # Estatísticas adicionais
            stats['availability_stats'] = self._get_availability_statistics(cursor)
            stats['city_distribution'] = self._get_city_distribution(cursor)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
        finally:
            conn.close()
    
    def _get_price_statistics(self, cursor) -> Dict[str, Any]:
        """Obtém estatísticas de preços"""
        try:
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
                return {
                    'avg_price': round(price_row[0], 2) if price_row[0] else 0,
                    'min_price': price_row[1] if price_row[1] else 0,
                    'max_price': price_row[2] if price_row[2] else 0,
                    'products_with_price': price_row[3] if price_row[3] else 0
                }
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de preços: {e}")
            return {}
    
    def _get_rating_statistics(self, cursor) -> Dict[str, Any]:
        """Obtém estatísticas de avaliações"""
        try:
            cursor.execute("""
                SELECT 
                    AVG(CAST(avaliacao AS REAL)) as avg_rating,
                    MAX(CAST(avaliacao AS REAL)) as max_rating,
                    MIN(CAST(avaliacao AS REAL)) as min_rating,
                    COUNT(*) as restaurants_with_rating
                FROM restaurants 
                WHERE avaliacao IS NOT NULL AND avaliacao != '' AND avaliacao != '0'
            """)
            
            rating_row = cursor.fetchone()
            if rating_row:
                return {
                    'avg_rating': round(rating_row[0], 2) if rating_row[0] else 0,
                    'max_rating': rating_row[1] if rating_row[1] else 0,
                    'min_rating': rating_row[2] if rating_row[2] else 0,
                    'restaurants_with_rating': rating_row[3] if rating_row[3] else 0
                }
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de avaliações: {e}")
            return {}
    
    def _get_top_categories(self, cursor, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém top categorias por número de restaurantes"""
        try:
            cursor.execute("""
                SELECT categoria, COUNT(*) as count, AVG(avaliacao) as avg_rating
                FROM restaurants 
                WHERE categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria 
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'categoria': row[0], 
                    'count': row[1],
                    'avg_rating': round(row[2], 2) if row[2] else 0
                } 
                for row in cursor.fetchall()
            ]
        except Exception as e:
            self.logger.error(f"Erro ao obter top categorias: {e}")
            return []
    
    def _get_availability_statistics(self, cursor) -> Dict[str, int]:
        """Obtém estatísticas de disponibilidade de produtos"""
        try:
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN disponivel = 1 THEN 1 ELSE 0 END) as available,
                    SUM(CASE WHEN disponivel = 0 THEN 1 ELSE 0 END) as unavailable,
                    COUNT(*) as total
                FROM products
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'available': row[0] or 0,
                    'unavailable': row[1] or 0,
                    'total': row[2] or 0,
                    'availability_rate': round((row[0] or 0) / (row[2] or 1) * 100, 2)
                }
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de disponibilidade: {e}")
            return {}
    
    def _get_city_distribution(self, cursor, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém distribuição de restaurantes por cidade"""
        try:
            cursor.execute("""
                SELECT city, COUNT(*) as count
                FROM restaurants 
                WHERE city IS NOT NULL AND city != ''
                GROUP BY city 
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {'city': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
        except Exception as e:
            self.logger.error(f"Erro ao obter distribuição por cidade: {e}")
            return []
    
    def get_category_insights(self, category: str) -> Dict[str, Any]:
        """Obtém insights detalhados sobre uma categoria específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            insights = {}
            
            # Informações básicas da categoria
            cursor.execute("""
                SELECT COUNT(*) as restaurant_count, AVG(avaliacao) as avg_rating
                FROM restaurants 
                WHERE categoria = ?
            """, (category,))
            
            basic_info = cursor.fetchone()
            if basic_info:
                insights['basic_info'] = {
                    'restaurant_count': basic_info[0],
                    'avg_rating': round(basic_info[1], 2) if basic_info[1] else 0
                }
            
            # Produtos mais populares da categoria
            cursor.execute("""
                SELECT p.nome, COUNT(*) as frequency, AVG(p.preco_numerico) as avg_price
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE r.categoria = ? AND p.preco_numerico > 0
                GROUP BY p.nome
                ORDER BY frequency DESC
                LIMIT 10
            """, (category,))
            
            insights['popular_products'] = [
                {
                    'product_name': row[0],
                    'frequency': row[1],
                    'avg_price': round(row[2], 2) if row[2] else 0
                }
                for row in cursor.fetchall()
            ]
            
            # Faixa de preços da categoria
            insights['price_distribution'] = self.get_price_distribution(category)
            
            # Top restaurantes da categoria
            cursor.execute("""
                SELECT nome, avaliacao, city
                FROM restaurants 
                WHERE categoria = ? AND avaliacao IS NOT NULL
                ORDER BY avaliacao DESC
                LIMIT 5
            """, (category,))
            
            insights['top_restaurants'] = [
                {
                    'name': row[0],
                    'rating': row[1],
                    'city': row[2]
                }
                for row in cursor.fetchall()
            ]
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Erro ao obter insights da categoria {category}: {e}")
            return {}
        finally:
            conn.close()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance do sistema de busca"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            metrics = {}
            
            # Tamanho do banco de dados
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            metrics['database_size_mb'] = round(db_size / (1024 * 1024), 2)
            
            # Número de índices
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            metrics['total_indexes'] = cursor.fetchone()[0]
            
            # Data da última atualização (aproximada)
            cursor.execute("SELECT MAX(extracted_at) FROM restaurants")
            last_update = cursor.fetchone()[0]
            metrics['last_update'] = last_update
            
            # Densidade de dados (campos preenchidos)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN avaliacao IS NOT NULL AND avaliacao != '' THEN 1 ELSE 0 END) as with_rating,
                    SUM(CASE WHEN endereco IS NOT NULL AND endereco != '' THEN 1 ELSE 0 END) as with_address
                FROM restaurants
            """)
            
            restaurant_density = cursor.fetchone()
            if restaurant_density:
                total = restaurant_density[0]
                metrics['data_density'] = {
                    'restaurants_with_rating': round((restaurant_density[1] / total * 100), 2) if total > 0 else 0,
                    'restaurants_with_address': round((restaurant_density[2] / total * 100), 2) if total > 0 else 0
                }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas de performance: {e}")
            return {}
        finally:
            conn.close()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Gera relatório resumido completo"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'database_statistics': self.get_database_statistics(),
                'popular_categories': self.get_popular_categories(5),
                'price_distribution': self.get_price_distribution(),
                'performance_metrics': self.get_performance_metrics()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }