#!/usr/bin/env python3
"""
Price Analysis - Detailed price analysis and cost-benefit reports
"""

from typing import Dict, Any, List
from pathlib import Path

from .reports_base import ReportsBase


class PriceAnalysis(ReportsBase):
    """Detailed price analysis and cost-benefit reporting"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Análise de Preços", session_stats, data_dir)
    
    def generate_price_analysis(self):
        """Generate comprehensive price analysis"""
        self.print_section_header("📈 ANÁLISE DETALHADA DE PREÇOS")
        
        # Price distribution
        self._show_price_distribution()
        
        # Category price analysis
        self._show_category_price_analysis()
        
        # Best value products
        self._show_best_value_analysis()
        
        # Price trends
        self._show_price_trends()
        
        # Outlier analysis
        self._show_outlier_analysis()
    
    def _show_price_distribution(self):
        """Show price distribution by ranges"""
        self.print_subsection_header("💰 DISTRIBUIÇÃO POR FAIXA DE PREÇO")
        
        try:
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
                    COUNT(*) as count,
                    AVG(price) as avg_price_in_range
                FROM products
                WHERE price > 0
                GROUP BY faixa_preco
                ORDER BY MIN(price)
            """
            
            price_ranges = self.safe_execute_query(query)
            
            if price_ranges:
                table_data = []
                total_products = sum(row['count'] for row in price_ranges)
                
                for range_data in price_ranges:
                    percentage = (range_data['count'] / total_products) * 100
                    table_data.append([
                        range_data['faixa_preco'],
                        range_data['count'],
                        self.format_percentage(percentage),
                        self.format_currency(range_data['avg_price_in_range'])
                    ])
                
                headers = ['Faixa de Preço', 'Produtos', 'Percentual', 'Preço Médio']
                self.format_table(table_data, headers)
                
                # Show summary statistics
                print(f"\n📊 Resumo da distribuição:")
                print(f"  Total de produtos analisados: {total_products:,}")
                
                # Most common price range
                most_common = max(price_ranges, key=lambda x: x['count'])
                print(f"  Faixa mais comum: {most_common['faixa_preco']} ({most_common['count']} produtos)")
                
        except Exception as e:
            self.show_error(f"Erro na distribuição de preços: {e}")
    
    def _show_category_price_analysis(self):
        """Show price analysis by category"""
        self.print_subsection_header("📊 ANÁLISE POR CATEGORIA (min. 5 produtos)")
        
        try:
            query = """
                SELECT 
                    category,
                    COUNT(*) as count,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price
                FROM products
                WHERE price > 0 AND category IS NOT NULL
                GROUP BY category
                HAVING COUNT(*) >= 5
                ORDER BY avg_price DESC
                LIMIT 15
            """
            
            category_analysis = self.safe_execute_query(query)
            
            if category_analysis:
                table_data = []
                for cat in category_analysis:
                    table_data.append([
                        cat['category'][:20],
                        cat['count'],
                        self.format_currency(cat['avg_price']),
                        self.format_currency(cat['min_price']),
                        self.format_currency(cat['max_price']),
                        self.format_currency(cat['std_price']) if cat['std_price'] else 'N/A'
                    ])
                
                headers = ['Categoria', 'Produtos', 'Preço Médio', 'Mínimo', 'Máximo', 'Desvio']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de categoria com preços encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise por categoria: {e}")
    
    def _show_best_value_analysis(self):
        """Show best value analysis"""
        self.print_subsection_header("🎯 MELHOR CUSTO-BENEFÍCIO")
        
        try:
            # Best value under R$ 25 with good rating
            query = """
                SELECT 
                    p.name,
                    p.price,
                    p.category,
                    r.name as restaurant_name,
                    r.rating,
                    (r.rating / p.price) as value_score
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND p.price <= 25 AND r.rating >= 4.0
                ORDER BY value_score DESC, r.rating DESC, p.price ASC
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
                        prod['rating'],
                        f"{prod['value_score']:.2f}"
                    ])
                
                headers = ['Produto', 'Preço', 'Categoria', 'Restaurante', 'Nota', 'Score']
                self.format_table(table_data, headers)
                
                print(f"\n💡 Score = Nota do Restaurante / Preço do Produto")
            else:
                print("Nenhum produto com bom custo-benefício encontrado")
            
            # Affordable quality options
            self._show_affordable_quality_options()
            
        except Exception as e:
            self.show_error(f"Erro na análise de custo-benefício: {e}")
    
    def _show_affordable_quality_options(self):
        """Show affordable options from high-rated restaurants"""
        self.print_subsection_header("💰 OPÇÕES ACESSÍVEIS EM RESTAURANTES BEM AVALIADOS")
        
        try:
            query = """
                SELECT 
                    p.name,
                    p.price,
                    p.category,
                    r.name as restaurant_name,
                    r.rating
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND p.price <= 15 AND r.rating >= 4.2
                ORDER BY p.price ASC, r.rating DESC
                LIMIT 10
            """
            
            affordable = self.safe_execute_query(query)
            
            if affordable:
                table_data = []
                for prod in affordable:
                    table_data.append([
                        prod['name'][:30],
                        self.format_currency(prod['price']),
                        prod['category'][:15] if prod['category'] else 'N/A',
                        prod['restaurant_name'][:25],
                        prod['rating']
                    ])
                
                headers = ['Produto', 'Preço', 'Categoria', 'Restaurante', 'Nota']
                self.format_table(table_data, headers)
            else:
                print("Nenhuma opção acessível encontrada")
                
        except Exception as e:
            self.show_error(f"Erro ao obter opções acessíveis: {e}")
    
    def _show_price_trends(self):
        """Show price trends and patterns"""
        self.print_subsection_header("📈 TENDÊNCIAS DE PREÇO")
        
        try:
            # Average price by restaurant rating
            rating_price_analysis = self.safe_execute_query("""
                SELECT 
                    CASE 
                        WHEN r.rating >= 4.5 THEN 'Excelente (4.5+)'
                        WHEN r.rating >= 4.0 THEN 'Muito Bom (4.0-4.4)'
                        WHEN r.rating >= 3.5 THEN 'Bom (3.5-3.9)'
                        WHEN r.rating >= 3.0 THEN 'Regular (3.0-3.4)'
                        ELSE 'Ruim (<3.0)'
                    END as rating_category,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_price
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND r.rating IS NOT NULL
                GROUP BY rating_category
                ORDER BY MIN(r.rating) DESC
            """)
            
            if rating_price_analysis:
                print("💫 Preço médio por faixa de avaliação do restaurante:")
                table_data = []
                for analysis in rating_price_analysis:
                    table_data.append([
                        analysis['rating_category'],
                        analysis['product_count'],
                        self.format_currency(analysis['avg_price'])
                    ])
                
                headers = ['Faixa de Avaliação', 'Produtos', 'Preço Médio']
                self.format_table(table_data, headers)
            
            # Price by city
            self._show_city_price_analysis()
            
        except Exception as e:
            self.show_error(f"Erro na análise de tendências: {e}")
    
    def _show_city_price_analysis(self):
        """Show price analysis by city"""
        try:
            city_price_analysis = self.safe_execute_query("""
                SELECT 
                    r.city,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_price,
                    MIN(p.price) as min_price,
                    MAX(p.price) as max_price
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND r.city IS NOT NULL
                GROUP BY r.city
                HAVING COUNT(p.id) >= 10
                ORDER BY avg_price DESC
                LIMIT 10
            """)
            
            if city_price_analysis:
                print(f"\n🌍 Preço médio por cidade (min. 10 produtos):")
                table_data = []
                for analysis in city_price_analysis:
                    table_data.append([
                        analysis['city'],
                        analysis['product_count'],
                        self.format_currency(analysis['avg_price']),
                        self.format_currency(analysis['min_price']),
                        self.format_currency(analysis['max_price'])
                    ])
                
                headers = ['Cidade', 'Produtos', 'Preço Médio', 'Mínimo', 'Máximo']
                self.format_table(table_data, headers)
                
        except Exception as e:
            self.show_error(f"Erro na análise por cidade: {e}")
    
    def _show_outlier_analysis(self):
        """Show price outlier analysis"""
        self.print_subsection_header("🔍 ANÁLISE DE VALORES ATÍPICOS")
        
        try:
            # Very expensive products (top 1%)
            total_products = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM products WHERE price > 0",
                fetch_one=True
            )
            
            if total_products and total_products['count'] > 0:
                top_1_percent = max(1, int(total_products['count'] * 0.01))
                
                expensive_outliers = self.safe_execute_query(f"""
                    SELECT 
                        p.name,
                        p.price,
                        p.category,
                        r.name as restaurant_name,
                        r.rating
                    FROM products p
                    JOIN restaurants r ON p.restaurant_id = r.id
                    WHERE p.price > 0
                    ORDER BY p.price DESC
                    LIMIT {top_1_percent}
                """)
                
                if expensive_outliers:
                    print(f"💎 Produtos mais caros (top 1% = {len(expensive_outliers)} produtos):")
                    table_data = []
                    for prod in expensive_outliers[:5]:  # Show only top 5
                        table_data.append([
                            prod['name'][:25],
                            self.format_currency(prod['price']),
                            prod['category'][:15] if prod['category'] else 'N/A',
                            prod['restaurant_name'][:20],
                            prod['rating'] or 'N/A'
                        ])
                    
                    headers = ['Produto', 'Preço', 'Categoria', 'Restaurante', 'Nota']
                    self.format_table(table_data, headers)
                    
                    if len(expensive_outliers) > 5:
                        print(f"  ... e mais {len(expensive_outliers) - 5} produtos")
            
            # Very cheap products that might be promotional
            cheap_products = self.safe_execute_query("""
                SELECT 
                    p.name,
                    p.price,
                    p.category,
                    r.name as restaurant_name,
                    r.rating
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0 AND p.price <= 5
                ORDER BY p.price ASC
                LIMIT 10
            """)
            
            if cheap_products:
                print(f"\n🏷️ Produtos muito baratos (≤ R$ 5.00):")
                table_data = []
                for prod in cheap_products:
                    table_data.append([
                        prod['name'][:25],
                        self.format_currency(prod['price']),
                        prod['category'][:15] if prod['category'] else 'N/A',
                        prod['restaurant_name'][:20],
                        prod['rating'] or 'N/A'
                    ])
                
                headers = ['Produto', 'Preço', 'Categoria', 'Restaurante', 'Nota']
                self.format_table(table_data, headers)
                
        except Exception as e:
            self.show_error(f"Erro na análise de valores atípicos: {e}")
    
    def generate_category_price_comparison(self, categories: List[str]):
        """Generate price comparison between specific categories"""
        self.print_section_header("🔄 COMPARAÇÃO DE PREÇOS ENTRE CATEGORIAS")
        
        try:
            for category in categories:
                category_stats = self.safe_execute_query("""
                    SELECT 
                        COUNT(*) as count,
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        STDDEV(price) as std_price
                    FROM products
                    WHERE category LIKE %s AND price > 0
                """, (f"%{category}%",), fetch_one=True)
                
                if category_stats and category_stats['count'] > 0:
                    print(f"\n📊 {category.upper()}:")
                    print(f"  Produtos: {category_stats['count']}")
                    print(f"  Preço médio: {self.format_currency(category_stats['avg_price'])}")
                    print(f"  Faixa: {self.format_currency(category_stats['min_price'])} - {self.format_currency(category_stats['max_price'])}")
                    print(f"  Desvio padrão: {self.format_currency(category_stats['std_price'])}")
                else:
                    print(f"\n❌ {category.upper()}: Nenhum produto encontrado")
                    
        except Exception as e:
            self.show_error(f"Erro na comparação de categorias: {e}")
    
    def export_price_analysis(self, format: str = 'csv') -> str:
        """
        Export price analysis data
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Get comprehensive price data
            query = """
                SELECT 
                    p.name,
                    p.price,
                    p.category,
                    r.name as restaurant_name,
                    r.category as restaurant_category,
                    r.rating,
                    r.city,
                    CASE 
                        WHEN p.price <= 10 THEN 'Até R$ 10'
                        WHEN p.price <= 20 THEN 'R$ 10 - R$ 20'
                        WHEN p.price <= 30 THEN 'R$ 20 - R$ 30'
                        WHEN p.price <= 50 THEN 'R$ 30 - R$ 50'
                        WHEN p.price <= 100 THEN 'R$ 50 - R$ 100'
                        ELSE 'Acima de R$ 100'
                    END as price_range,
                    (r.rating / p.price) as value_score
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.price > 0
                ORDER BY p.price DESC
            """
            
            price_data = self.safe_execute_query(query)
            
            if not price_data:
                raise ValueError("Nenhum dado de preço encontrado")
            
            # Convert to list of dicts
            data = [dict(item) for item in price_data]
            
            if format.lower() == 'json':
                # Create comprehensive JSON report
                stats = self.get_price_analysis_statistics()
                report_data = {
                    'metadata': self.get_base_statistics(),
                    'summary': stats.get('price_stats', {}),
                    'analysis': {
                        'distribution': stats.get('price_distribution', []),
                        'category_analysis': stats.get('category_analysis', []),
                        'outliers': stats.get('outliers', {})
                    },
                    'products': data
                }
                filepath = self.export_to_json(report_data, 'analise_precos')
            else:
                # Export as CSV
                fieldnames = ['name', 'price', 'category', 'restaurant_name', 
                            'restaurant_category', 'rating', 'city', 'price_range', 'value_score']
                filepath = self.export_to_csv(data, 'analise_precos', fieldnames)
            
            return str(filepath)
            
        except Exception as e:
            self.show_error(f"Erro ao exportar análise: {e}")
            return ""
    
    def get_price_analysis_statistics(self) -> Dict[str, Any]:
        """Get price analysis statistics"""
        stats = self.get_base_statistics()
        
        try:
            # Basic price statistics
            price_stats = self.safe_execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price
                FROM products
                WHERE price > 0
            """, fetch_one=True)
            
            stats['price_stats'] = dict(price_stats) if price_stats else {}
            
            # Price distribution
            distribution = self.safe_execute_query("""
                SELECT 
                    CASE 
                        WHEN price <= 10 THEN 'Até R$ 10'
                        WHEN price <= 20 THEN 'R$ 10 - R$ 20'
                        WHEN price <= 30 THEN 'R$ 20 - R$ 30'
                        WHEN price <= 50 THEN 'R$ 30 - R$ 50'
                        WHEN price <= 100 THEN 'R$ 50 - R$ 100'
                        ELSE 'Acima de R$ 100'
                    END as price_range,
                    COUNT(*) as count
                FROM products
                WHERE price > 0
                GROUP BY price_range
                ORDER BY MIN(price)
            """)
            
            stats['price_distribution'] = [dict(item) for item in (distribution or [])]
            
            # Category analysis
            category_analysis = self.safe_execute_query("""
                SELECT 
                    category,
                    COUNT(*) as count,
                    AVG(price) as avg_price
                FROM products
                WHERE price > 0 AND category IS NOT NULL
                GROUP BY category
                HAVING COUNT(*) >= 5
                ORDER BY avg_price DESC
                LIMIT 10
            """)
            
            stats['category_analysis'] = [dict(item) for item in (category_analysis or [])]
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats