#!/usr/bin/env python3
"""
Restaurants Report - Restaurant analysis and statistics
"""

from typing import Dict, Any, List
from pathlib import Path

from .reports_base import ReportsBase


class RestaurantsReport(ReportsBase):
    """Restaurant analysis and statistics reporting"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatório de Restaurantes", session_stats, data_dir)
    
    def generate_restaurants_report(self):
        """Generate comprehensive restaurants report"""
        self.print_section_header("🏪 RELATÓRIO DE RESTAURANTES")
        
        # Basic statistics
        self._show_basic_statistics()
        
        # Distribution by city
        self._show_city_distribution()
        
        # Distribution by category
        self._show_category_distribution()
        
        # Top rated restaurants
        self._show_top_rated_restaurants()
        
        # Delivery time analysis
        self._show_delivery_analysis()
        
        # Rating analysis
        self._show_rating_analysis()
    
    def _show_basic_statistics(self):
        """Show basic restaurant statistics"""
        try:
            total = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM restaurants",
                fetch_one=True
            )
            
            cities_count = self.safe_execute_query(
                "SELECT COUNT(DISTINCT city) as cities FROM restaurants WHERE city IS NOT NULL",
                fetch_one=True
            )
            
            categories_count = self.safe_execute_query(
                "SELECT COUNT(DISTINCT category) as categories FROM restaurants WHERE category IS NOT NULL",
                fetch_one=True
            )
            
            if total:
                print(f"📋 Total de restaurantes: {total['total']:,}")
            if cities_count:
                print(f"🌍 Cidades atendidas: {cities_count['cities']}")
            if categories_count:
                print(f"🏷️ Categorias disponíveis: {categories_count['categories']}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas básicas: {e}")
    
    def _show_city_distribution(self):
        """Show restaurant distribution by city"""
        self.print_subsection_header("🌍 TOP 10 CIDADES POR NÚMERO DE RESTAURANTES")
        
        try:
            cities = self.get_top_items('restaurants', 'city', limit=10, 
                                      where_clause='city IS NOT NULL')
            
            if cities:
                table_data = []
                for i, city in enumerate(cities, 1):
                    table_data.append([i, city['city'], city['count']])
                
                headers = ['Pos', 'Cidade', 'Restaurantes']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de distribuição por cidade encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter distribuição por cidade: {e}")
    
    def _show_category_distribution(self):
        """Show restaurant distribution by category"""
        self.print_subsection_header("🏷️ TOP 10 CATEGORIAS POR NÚMERO DE RESTAURANTES")
        
        try:
            categories = self.get_top_items('restaurants', 'category', limit=10,
                                          where_clause='category IS NOT NULL')
            
            if categories:
                table_data = []
                for i, cat in enumerate(categories, 1):
                    table_data.append([i, cat['category'], cat['count']])
                
                headers = ['Pos', 'Categoria', 'Restaurantes']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de distribuição por categoria encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter distribuição por categoria: {e}")
    
    def _show_top_rated_restaurants(self):
        """Show top rated restaurants"""
        self.print_subsection_header("⭐ TOP 10 RESTAURANTES MELHOR AVALIADOS")
        
        try:
            query = """
                SELECT name, category, rating, delivery_time, delivery_fee, city
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
                ORDER BY rating DESC, name ASC
                LIMIT 10
            """
            
            top_rated = self.safe_execute_query(query)
            
            if top_rated:
                table_data = []
                for rest in top_rated:
                    table_data.append([
                        rest['name'][:25],
                        rest['category'][:20] if rest['category'] else 'N/A',
                        rest['rating'],
                        rest['delivery_time'] or 'N/A',
                        rest['delivery_fee'] or 'N/A',
                        rest['city'] or 'N/A'
                    ])
                
                headers = ['Nome', 'Categoria', 'Nota', 'Tempo', 'Taxa', 'Cidade']
                self.format_table(table_data, headers)
            else:
                print("Nenhum restaurante avaliado encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter restaurantes bem avaliados: {e}")
    
    def _show_delivery_analysis(self):
        """Show delivery time analysis"""
        self.print_subsection_header("🕐 ANÁLISE DE TEMPO DE ENTREGA")
        
        try:
            query = """
                SELECT 
                    CASE 
                        WHEN delivery_time LIKE '%10%' OR delivery_time LIKE '%15%' THEN 'Muito rápido (≤15min)'
                        WHEN delivery_time LIKE '%20%' OR delivery_time LIKE '%25%' OR delivery_time LIKE '%30%' THEN 'Rápido (15-30min)'
                        WHEN delivery_time LIKE '%35%' OR delivery_time LIKE '%40%' OR delivery_time LIKE '%45%' THEN 'Médio (30-45min)'
                        WHEN delivery_time LIKE '%50%' OR delivery_time LIKE '%60%' THEN 'Lento (45-60min)'
                        ELSE 'Muito lento (>60min)'
                    END as tempo_categoria,
                    COUNT(*) as count
                FROM restaurants
                WHERE delivery_time IS NOT NULL
                GROUP BY tempo_categoria
                ORDER BY count DESC
            """
            
            delivery_analysis = self.safe_execute_query(query)
            
            if delivery_analysis:
                table_data = []
                total_restaurants = sum(row['count'] for row in delivery_analysis)
                
                for analysis in delivery_analysis:
                    percentage = (analysis['count'] / total_restaurants) * 100
                    table_data.append([
                        analysis['tempo_categoria'], 
                        analysis['count'],
                        self.format_percentage(percentage)
                    ])
                
                headers = ['Tempo', 'Restaurantes', 'Percentual']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de tempo de entrega encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise de tempo de entrega: {e}")
    
    def _show_rating_analysis(self):
        """Show rating distribution analysis"""
        self.print_subsection_header("📊 ANÁLISE DE AVALIAÇÕES")
        
        try:
            # Rating statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_with_rating,
                    AVG(rating) as avg_rating,
                    MIN(rating) as min_rating,
                    MAX(rating) as max_rating,
                    STDDEV(rating) as std_rating
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
            """
            
            stats = self.safe_execute_query(stats_query, fetch_one=True)
            
            if stats and stats['total_with_rating'] > 0:
                print(f"  Restaurantes com avaliação: {stats['total_with_rating']:,}")
                print(f"  Avaliação média: {stats['avg_rating']:.2f}")
                print(f"  Avaliação mínima: {stats['min_rating']:.2f}")
                print(f"  Avaliação máxima: {stats['max_rating']:.2f}")
                print(f"  Desvio padrão: {stats['std_rating']:.2f}")
            
            # Rating distribution
            distribution_query = """
                SELECT 
                    CASE 
                        WHEN rating >= 4.5 THEN 'Excelente (4.5-5.0)'
                        WHEN rating >= 4.0 THEN 'Muito bom (4.0-4.4)'
                        WHEN rating >= 3.5 THEN 'Bom (3.5-3.9)'
                        WHEN rating >= 3.0 THEN 'Regular (3.0-3.4)'
                        ELSE 'Ruim (<3.0)'
                    END as rating_category,
                    COUNT(*) as count
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
                GROUP BY rating_category
                ORDER BY MIN(rating) DESC
            """
            
            distribution = self.safe_execute_query(distribution_query)
            
            if distribution:
                print(f"\n📈 Distribuição por faixa de avaliação:")
                table_data = []
                total = sum(row['count'] for row in distribution)
                
                for dist in distribution:
                    percentage = (dist['count'] / total) * 100
                    table_data.append([
                        dist['rating_category'],
                        dist['count'],
                        self.format_percentage(percentage)
                    ])
                
                headers = ['Faixa', 'Restaurantes', 'Percentual']
                self.format_table(table_data, headers)
                
        except Exception as e:
            self.show_error(f"Erro na análise de avaliações: {e}")
    
    def generate_city_specific_report(self, city: str):
        """Generate report for a specific city"""
        self.print_section_header(f"🏪 RELATÓRIO DE RESTAURANTES - {city.upper()}")
        
        try:
            # Basic statistics for the city
            total = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM restaurants WHERE city LIKE %s",
                (f"%{city}%",), fetch_one=True
            )
            
            if total and total['total'] > 0:
                print(f"📋 Total de restaurantes em {city}: {total['total']}")
                
                # Top categories in this city
                categories = self.safe_execute_query("""
                    SELECT category, COUNT(*) as count
                    FROM restaurants
                    WHERE city LIKE %s AND category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                    LIMIT 10
                """, (f"%{city}%",))
                
                if categories:
                    self.print_subsection_header(f"🏷️ TOP CATEGORIAS EM {city.upper()}")
                    table_data = []
                    for i, cat in enumerate(categories, 1):
                        table_data.append([i, cat['category'], cat['count']])
                    
                    headers = ['Pos', 'Categoria', 'Restaurantes']
                    self.format_table(table_data, headers)
                
                # Best rated in this city
                top_rated = self.safe_execute_query("""
                    SELECT name, category, rating, delivery_time, delivery_fee
                    FROM restaurants
                    WHERE city LIKE %s AND rating IS NOT NULL AND rating > 0
                    ORDER BY rating DESC, name ASC
                    LIMIT 10
                """, (f"%{city}%",))
                
                if top_rated:
                    self.print_subsection_header(f"⭐ MELHOR AVALIADOS EM {city.upper()}")
                    table_data = []
                    for rest in top_rated:
                        table_data.append([
                            rest['name'][:30],
                            rest['category'][:20] if rest['category'] else 'N/A',
                            rest['rating'],
                            rest['delivery_time'] or 'N/A',
                            rest['delivery_fee'] or 'N/A'
                        ])
                    
                    headers = ['Nome', 'Categoria', 'Nota', 'Tempo', 'Taxa']
                    self.format_table(table_data, headers)
            else:
                print(f"❌ Nenhum restaurante encontrado em {city}")
                
        except Exception as e:
            self.show_error(f"Erro ao gerar relatório para {city}: {e}")
    
    def export_restaurants_report(self, format: str = 'csv') -> str:
        """
        Export restaurants report data
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Get all restaurant data
            query = """
                SELECT 
                    r.name, 
                    r.category, 
                    r.rating, 
                    r.delivery_time, 
                    r.delivery_fee,
                    r.distance, 
                    r.city, 
                    r.address, 
                    r.created_at,
                    COUNT(p.id) as product_count
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                GROUP BY r.id, r.name, r.category, r.rating, r.delivery_time, 
                         r.delivery_fee, r.distance, r.city, r.address, r.created_at
                ORDER BY r.name
            """
            
            restaurants = self.safe_execute_query(query)
            
            if not restaurants:
                raise ValueError("Nenhum dado de restaurante encontrado")
            
            # Convert to list of dicts
            data = [dict(rest) for rest in restaurants]
            
            if format.lower() == 'json':
                # Create comprehensive JSON report
                stats = self.get_restaurants_statistics()
                report_data = {
                    'metadata': self.get_base_statistics(),
                    'summary': stats.get('restaurants_stats', {}),
                    'restaurants': data
                }
                filepath = self.export_to_json(report_data, 'restaurantes_relatorio')
            else:
                # Export as CSV
                fieldnames = ['name', 'category', 'rating', 'delivery_time', 'delivery_fee',
                            'distance', 'city', 'address', 'created_at', 'product_count']
                filepath = self.export_to_csv(data, 'restaurantes_relatorio', fieldnames)
            
            return str(filepath)
            
        except Exception as e:
            self.show_error(f"Erro ao exportar relatório: {e}")
            return ""
    
    def get_restaurants_statistics(self) -> Dict[str, Any]:
        """Get restaurants report statistics"""
        stats = self.get_base_statistics()
        
        try:
            # Basic counts
            total = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM restaurants",
                fetch_one=True
            )
            
            with_rating = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM restaurants WHERE rating IS NOT NULL AND rating > 0",
                fetch_one=True
            )
            
            cities = self.safe_execute_query(
                "SELECT COUNT(DISTINCT city) as count FROM restaurants WHERE city IS NOT NULL",
                fetch_one=True
            )
            
            # Rating statistics
            rating_stats = self.safe_execute_query("""
                SELECT 
                    AVG(rating) as avg_rating,
                    MIN(rating) as min_rating,
                    MAX(rating) as max_rating
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
            """, fetch_one=True)
            
            stats['restaurants_stats'] = {
                'total_restaurants': total['count'] if total else 0,
                'with_rating': with_rating['count'] if with_rating else 0,
                'cities_count': cities['count'] if cities else 0,
                'avg_rating': float(rating_stats['avg_rating']) if rating_stats and rating_stats['avg_rating'] else 0,
                'min_rating': float(rating_stats['min_rating']) if rating_stats and rating_stats['min_rating'] else 0,
                'max_rating': float(rating_stats['max_rating']) if rating_stats and rating_stats['max_rating'] else 0
            }
            
            # Recent activity
            recent_data = self.get_date_range_data('restaurants', 'created_at', 7)
            stats['recent_activity'] = recent_data
            
            # Top cities
            top_cities = self.get_top_items('restaurants', 'city', limit=5, 
                                          where_clause='city IS NOT NULL')
            stats['top_cities'] = [dict(city) for city in (top_cities or [])]
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats