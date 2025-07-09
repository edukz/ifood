#!/usr/bin/env python3
"""
Products Report - Product analysis and statistics
"""

from typing import Dict, Any, List
from pathlib import Path

from .reports_base import ReportsBase


class ProductsReport(ReportsBase):
    """Product analysis and statistics reporting"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatório de Produtos", session_stats, data_dir)
    
    def generate_products_report(self):
        """Generate comprehensive products report"""
        self.print_section_header("🍕 RELATÓRIO DE PRODUTOS")
        
        # Basic statistics
        self._show_basic_statistics()
        
        # Price analysis
        self._show_price_analysis()
        
        # Products by category
        self._show_category_analysis()
        
        # Top restaurants by product count
        self._show_restaurant_analysis()
        
        # Most expensive products
        self._show_expensive_products()
    
    def _show_basic_statistics(self):
        """Show basic product statistics"""
        try:
            total = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM products",
                fetch_one=True
            )
            
            categories_count = self.safe_execute_query(
                "SELECT COUNT(DISTINCT category) as categories FROM products WHERE category IS NOT NULL",
                fetch_one=True
            )
            
            restaurants_count = self.safe_execute_query(
                "SELECT COUNT(DISTINCT restaurant_id) as restaurants FROM products",
                fetch_one=True
            )
            
            if total:
                print(f"📋 Total de produtos: {total['total']:,}")
            if categories_count:
                print(f"🏷️ Categorias de produtos: {categories_count['categories']}")
            if restaurants_count:
                print(f"🏪 Restaurantes com produtos: {restaurants_count['restaurants']}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas básicas: {e}")
    
    def _show_price_analysis(self):
        """Show product price analysis"""
        self.print_subsection_header("💰 ANÁLISE DE PREÇOS")
        
        try:
            price_stats = self.safe_execute_query("""
                SELECT 
                    COUNT(*) as total,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price
                FROM products
                WHERE price > 0
            """, fetch_one=True)
            
            if price_stats and price_stats['total'] > 0:
                print(f"  Produtos com preço: {price_stats['total']:,}")
                print(f"  Preço médio: {self.format_currency(price_stats['avg_price'])}")
                print(f"  Preço mínimo: {self.format_currency(price_stats['min_price'])}")
                print(f"  Preço máximo: {self.format_currency(price_stats['max_price'])}")
                print(f"  Desvio padrão: {self.format_currency(price_stats['std_price'])}")
            else:
                print("Nenhum produto com preço encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise de preços: {e}")
    
    def _show_category_analysis(self):
        """Show product analysis by category"""
        self.print_subsection_header("🏷️ TOP 15 CATEGORIAS DE PRODUTOS")
        
        try:
            query = """
                SELECT category, COUNT(*) as count, AVG(price) as avg_price
                FROM products
                WHERE category IS NOT NULL AND price > 0
                GROUP BY category
                ORDER BY count DESC
                LIMIT 15
            """
            
            categories = self.safe_execute_query(query)
            
            if categories:
                table_data = []
                for i, cat in enumerate(categories, 1):
                    table_data.append([
                        i,
                        cat['category'],
                        cat['count'],
                        self.format_currency(cat['avg_price'])
                    ])
                
                headers = ['Pos', 'Categoria', 'Produtos', 'Preço Médio']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de categoria encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise por categoria: {e}")
    
    def _show_restaurant_analysis(self):
        """Show restaurants with most products"""
        self.print_subsection_header("🏪 TOP 10 RESTAURANTES COM MAIS PRODUTOS")
        
        try:
            query = """
                SELECT r.name, r.category, COUNT(p.id) as product_count
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                GROUP BY r.id, r.name, r.category
                HAVING product_count > 0
                ORDER BY product_count DESC
                LIMIT 10
            """
            
            top_restaurants = self.safe_execute_query(query)
            
            if top_restaurants:
                table_data = []
                for i, rest in enumerate(top_restaurants, 1):
                    table_data.append([
                        i,
                        rest['name'][:30],
                        rest['category'][:20] if rest['category'] else 'N/A',
                        rest['product_count']
                    ])
                
                headers = ['Pos', 'Restaurante', 'Categoria', 'Produtos']
                self.format_table(table_data, headers)
            else:
                print("Nenhum restaurante com produtos encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise de restaurantes: {e}")
    
    def _show_expensive_products(self):
        """Show most expensive products"""
        self.print_subsection_header("💎 TOP 10 PRODUTOS MAIS CAROS")
        
        try:
            query = """
                SELECT p.name, p.price, p.category, r.name as restaurant_name
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0
                ORDER BY p.price DESC
                LIMIT 10
            """
            
            expensive = self.safe_execute_query(query)
            
            if expensive:
                table_data = []
                for i, prod in enumerate(expensive, 1):
                    table_data.append([
                        i,
                        prod['name'][:25],
                        self.format_currency(prod['price']),
                        prod['category'][:15] if prod['category'] else 'N/A',
                        prod['restaurant_name'][:20]
                    ])
                
                headers = ['Pos', 'Produto', 'Preço', 'Categoria', 'Restaurante']
                self.format_table(table_data, headers)
            else:
                print("Nenhum produto caro encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter produtos caros: {e}")
    
    def generate_price_distribution_report(self):
        """Generate detailed price distribution report"""
        self.print_section_header("📊 DISTRIBUIÇÃO DETALHADA DE PREÇOS")
        
        try:
            # Price ranges
            query = """
                SELECT 
                    CASE 
                        WHEN price <= 10 THEN 'Até R$ 10'
                        WHEN price <= 20 THEN 'R$ 10 - R$ 20'
                        WHEN price <= 30 THEN 'R$ 20 - R$ 30'
                        WHEN price <= 50 THEN 'R$ 30 - R$ 50'
                        WHEN price <= 100 THEN 'R$ 50 - R$ 100'
                        ELSE 'Acima de R$ 100'
                    END as faixa_preco,
                    COUNT(*) as count
                FROM products
                WHERE price > 0
                GROUP BY faixa_preco
                ORDER BY MIN(price)
            """
            
            price_ranges = self.safe_execute_query(query)
            
            if price_ranges:
                self.print_subsection_header("💰 DISTRIBUIÇÃO POR FAIXA DE PREÇO")
                table_data = []
                total_products = sum(row['count'] for row in price_ranges)
                
                for range_data in price_ranges:
                    percentage = (range_data['count'] / total_products) * 100
                    table_data.append([
                        range_data['faixa_preco'],
                        range_data['count'],
                        self.format_percentage(percentage)
                    ])
                
                headers = ['Faixa de Preço', 'Produtos', 'Percentual']
                self.format_table(table_data, headers)
            
            # Best value products
            self._show_best_value_products()
            
        except Exception as e:
            self.show_error(f"Erro na distribuição de preços: {e}")
    
    def _show_best_value_products(self):
        """Show best value products"""
        self.print_subsection_header("🎯 MELHOR CUSTO-BENEFÍCIO (≤R$ 25, nota ≥4.0)")
        
        try:
            query = """
                SELECT 
                    p.category,
                    p.name,
                    p.price,
                    r.name as restaurant_name,
                    r.rating
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND p.price <= 25 AND r.rating >= 4.0
                ORDER BY r.rating DESC, p.price ASC
                LIMIT 15
            """
            
            best_value = self.safe_execute_query(query)
            
            if best_value:
                table_data = []
                for prod in best_value:
                    table_data.append([
                        prod['name'][:25],
                        self.format_currency(prod['price']),
                        prod['category'][:15] if prod['category'] else 'N/A',
                        prod['restaurant_name'][:20],
                        prod['rating']
                    ])
                
                headers = ['Produto', 'Preço', 'Categoria', 'Restaurante', 'Nota']
                self.format_table(table_data, headers)
            else:
                print("Nenhum produto com bom custo-benefício encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter produtos com melhor custo-benefício: {e}")
    
    def generate_category_detailed_report(self, category: str):
        """Generate detailed report for a specific category"""
        self.print_section_header(f"🍕 RELATÓRIO DETALHADO - {category.upper()}")
        
        try:
            # Basic statistics for the category
            total = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM products WHERE category LIKE %s",
                (f"%{category}%",), fetch_one=True
            )
            
            if total and total['total'] > 0:
                print(f"📋 Total de produtos em {category}: {total['total']}")
                
                # Price statistics for category
                price_stats = self.safe_execute_query("""
                    SELECT 
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM products
                    WHERE category LIKE %s AND price > 0
                """, (f"%{category}%",), fetch_one=True)
                
                if price_stats:
                    print(f"💰 Preço médio: {self.format_currency(price_stats['avg_price'])}")
                    print(f"💰 Faixa de preços: {self.format_currency(price_stats['min_price'])} - {self.format_currency(price_stats['max_price'])}")
                
                # Top products in category
                top_products = self.safe_execute_query("""
                    SELECT p.name, p.price, r.name as restaurant_name, r.rating
                    FROM products p
                    JOIN restaurants r ON p.restaurant_id = r.id
                    WHERE p.category LIKE %s AND p.price > 0
                    ORDER BY r.rating DESC, p.price ASC
                    LIMIT 10
                """, (f"%{category}%",))
                
                if top_products:
                    self.print_subsection_header(f"🏆 MELHORES PRODUTOS EM {category.upper()}")
                    table_data = []
                    for prod in top_products:
                        table_data.append([
                            prod['name'][:30],
                            self.format_currency(prod['price']),
                            prod['restaurant_name'][:25],
                            prod['rating'] or 'N/A'
                        ])
                    
                    headers = ['Produto', 'Preço', 'Restaurante', 'Nota']
                    self.format_table(table_data, headers)
            else:
                print(f"❌ Nenhum produto encontrado na categoria {category}")
                
        except Exception as e:
            self.show_error(f"Erro ao gerar relatório para categoria {category}: {e}")
    
    def export_products_report(self, format: str = 'csv') -> str:
        """
        Export products report data
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Get all product data
            query = """
                SELECT 
                    p.name, 
                    p.price, 
                    p.category, 
                    p.description,
                    r.name as restaurant_name, 
                    r.category as restaurant_category,
                    r.rating as restaurant_rating,
                    r.city as restaurant_city,
                    p.created_at
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                ORDER BY p.name
            """
            
            products = self.safe_execute_query(query)
            
            if not products:
                raise ValueError("Nenhum dado de produto encontrado")
            
            # Convert to list of dicts
            data = [dict(prod) for prod in products]
            
            if format.lower() == 'json':
                # Create comprehensive JSON report
                stats = self.get_products_statistics()
                report_data = {
                    'metadata': self.get_base_statistics(),
                    'summary': stats.get('products_stats', {}),
                    'products': data
                }
                filepath = self.export_to_json(report_data, 'produtos_relatorio')
            else:
                # Export as CSV
                fieldnames = ['name', 'price', 'category', 'description',
                            'restaurant_name', 'restaurant_category', 
                            'restaurant_rating', 'restaurant_city', 'created_at']
                filepath = self.export_to_csv(data, 'produtos_relatorio', fieldnames)
            
            return str(filepath)
            
        except Exception as e:
            self.show_error(f"Erro ao exportar relatório: {e}")
            return ""
    
    def get_products_statistics(self) -> Dict[str, Any]:
        """Get products report statistics"""
        stats = self.get_base_statistics()
        
        try:
            # Basic counts
            total = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM products",
                fetch_one=True
            )
            
            with_price = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM products WHERE price > 0",
                fetch_one=True
            )
            
            categories = self.safe_execute_query(
                "SELECT COUNT(DISTINCT category) as count FROM products WHERE category IS NOT NULL",
                fetch_one=True
            )
            
            # Price statistics
            price_stats = self.safe_execute_query("""
                SELECT 
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price
                FROM products
                WHERE price > 0
            """, fetch_one=True)
            
            stats['products_stats'] = {
                'total_products': total['count'] if total else 0,
                'with_price': with_price['count'] if with_price else 0,
                'categories_count': categories['count'] if categories else 0,
                'avg_price': float(price_stats['avg_price']) if price_stats and price_stats['avg_price'] else 0,
                'min_price': float(price_stats['min_price']) if price_stats and price_stats['min_price'] else 0,
                'max_price': float(price_stats['max_price']) if price_stats and price_stats['max_price'] else 0,
                'std_price': float(price_stats['std_price']) if price_stats and price_stats['std_price'] else 0
            }
            
            # Recent activity
            recent_data = self.get_date_range_data('products', 'created_at', 7)
            stats['recent_activity'] = recent_data
            
            # Top categories
            top_categories = self.get_top_items('products', 'category', limit=5,
                                              where_clause='category IS NOT NULL')
            stats['top_categories'] = [dict(cat) for cat in (top_categories or [])]
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats