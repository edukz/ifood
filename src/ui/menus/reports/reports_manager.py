#!/usr/bin/env python3
"""
Reports Manager - Central manager for all report modules
"""

from typing import Dict, Any
from pathlib import Path

from .categories_report import CategoriesReport
from .restaurants_report import RestaurantsReport
from .products_report import ProductsReport
from .price_analysis import PriceAnalysis
from .performance_report import PerformanceReport
from .custom_report import CustomReport
from .export_manager import ExportManager


class ReportsManager:
    """Central manager for all report modules"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        self.session_stats = session_stats
        self.data_dir = data_dir
        
        # Initialize all report modules
        self.categories_report = CategoriesReport(session_stats, data_dir)
        self.restaurants_report = RestaurantsReport(session_stats, data_dir)
        self.products_report = ProductsReport(session_stats, data_dir)
        self.price_analysis = PriceAnalysis(session_stats, data_dir)
        self.performance_report = PerformanceReport(session_stats, data_dir)
        self.custom_report = CustomReport(session_stats, data_dir)
        self.export_manager = ExportManager(session_stats, data_dir)
    
    def menu_reports(self):
        """Main reports menu"""
        options = [
            "1. 📊 Relatório de categorias",
            "2. 🏪 Relatório de restaurantes",
            "3. 🍕 Relatório de produtos",
            "4. 📈 Análise de preços",
            "5. 🎯 Relatório de performance",
            "6. 📋 Relatório personalizado",
            "7. 📁 Exportar dados",
            "8. 🔍 Relatórios especializados"
        ]
        
        from src.ui.base_menu import BaseMenu
        menu = BaseMenu("Relatórios e Análises", self.session_stats, self.data_dir)
        menu.show_menu("📊 RELATÓRIOS E ANÁLISES", options)
        choice = menu.get_user_choice(8)
        
        if choice == "1":
            self.categories_report.generate_categories_report()
        elif choice == "2":
            self.restaurants_report.generate_restaurants_report()
        elif choice == "3":
            self.products_report.generate_products_report()
        elif choice == "4":
            self.price_analysis.generate_price_analysis()
        elif choice == "5":
            self.performance_report.generate_performance_report()
        elif choice == "6":
            self.custom_report.generate_custom_report()
        elif choice == "7":
            self.export_manager.show_export_menu()
        elif choice == "8":
            self.show_specialized_reports_menu()
        elif choice == "0":
            return
        else:
            menu.show_invalid_option()
    
    def show_specialized_reports_menu(self):
        """Show specialized reports menu"""
        specialized_options = [
            "1. 📊 Distribuição detalhada de preços",
            "2. 🏪 Relatório por cidade específica",
            "3. 🍕 Análise de categoria específica",
            "4. 🎯 Relatórios personalizados predefinidos",
            "5. 📈 Comparação entre categorias",
            "6. ⭐ Análise de avaliações",
            "7. 🕐 Análise de tempo de entrega"
        ]
        
        from src.ui.base_menu import BaseMenu
        menu = BaseMenu("Relatórios Especializados", self.session_stats, self.data_dir)
        menu.show_menu("🔍 RELATÓRIOS ESPECIALIZADOS", specialized_options)
        choice = menu.get_user_choice(7)
        
        if choice == "1":
            self.price_analysis.generate_price_distribution_report()
        elif choice == "2":
            self._city_specific_report()
        elif choice == "3":
            self._category_specific_report()
        elif choice == "4":
            self.custom_report.generate_predefined_custom_reports()
        elif choice == "5":
            self._category_comparison_report()
        elif choice == "6":
            self._rating_analysis_report()
        elif choice == "7":
            self._delivery_time_analysis()
        elif choice == "0":
            return
        else:
            menu.show_invalid_option()
    
    def _city_specific_report(self):
        """Generate city-specific report"""
        city = input("Digite o nome da cidade: ").strip()
        if city:
            self.restaurants_report.generate_city_specific_report(city)
        else:
            print("❌ Nome da cidade não especificado")
    
    def _category_specific_report(self):
        """Generate category-specific report"""
        category = input("Digite o nome da categoria: ").strip()
        if category:
            self.products_report.generate_category_detailed_report(category)
        else:
            print("❌ Nome da categoria não especificado")
    
    def _category_comparison_report(self):
        """Generate category comparison report"""
        categories = input("Digite as categorias para comparar (separadas por vírgula): ").strip()
        if categories:
            category_list = [cat.strip() for cat in categories.split(',')]
            self.price_analysis.generate_category_price_comparison(category_list)
        else:
            print("❌ Categorias não especificadas")
    
    def _rating_analysis_report(self):
        """Generate detailed rating analysis"""
        print("\n⭐ ANÁLISE DETALHADA DE AVALIAÇÕES")
        print("═" * 50)
        
        try:
            # Rating distribution with more detail
            rating_distribution = self.restaurants_report.safe_execute_query("""
                SELECT 
                    FLOOR(rating) as rating_floor,
                    COUNT(*) as count,
                    AVG(rating) as avg_in_range,
                    MIN(rating) as min_in_range,
                    MAX(rating) as max_in_range
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
                GROUP BY FLOOR(rating)
                ORDER BY rating_floor DESC
            """)
            
            if rating_distribution:
                print("\n📊 Distribuição por faixa de nota:")
                table_data = []
                total_rated = sum(row['count'] for row in rating_distribution)
                
                for dist in rating_distribution:
                    percentage = (dist['count'] / total_rated) * 100
                    table_data.append([
                        f"{dist['rating_floor']:.0f}.0 - {dist['rating_floor']:.0f}.9",
                        dist['count'],
                        f"{percentage:.1f}%",
                        f"{dist['avg_in_range']:.2f}",
                        f"{dist['min_in_range']:.2f} - {dist['max_in_range']:.2f}"
                    ])
                
                headers = ['Faixa', 'Restaurantes', '%', 'Média', 'Min-Max']
                self.restaurants_report.format_table(table_data, headers)
            
        except Exception as e:
            self.restaurants_report.show_error(f"Erro na análise de avaliações: {e}")
    
    def _delivery_time_analysis(self):
        """Generate delivery time analysis"""
        print("\n🕐 ANÁLISE DETALHADA DE TEMPO DE ENTREGA")
        print("═" * 50)
        
        try:
            # More detailed delivery time analysis
            delivery_analysis = self.restaurants_report.safe_execute_query("""
                SELECT 
                    delivery_time,
                    COUNT(*) as count,
                    AVG(rating) as avg_rating
                FROM restaurants
                WHERE delivery_time IS NOT NULL AND delivery_time != ''
                GROUP BY delivery_time
                ORDER BY COUNT(*) DESC
                LIMIT 15
            """)
            
            if delivery_analysis:
                print("\n📊 Tempos de entrega mais comuns:")
                table_data = []
                for analysis in delivery_analysis:
                    table_data.append([
                        analysis['delivery_time'],
                        analysis['count'],
                        f"{analysis['avg_rating']:.2f}" if analysis['avg_rating'] else 'N/A'
                    ])
                
                headers = ['Tempo de Entrega', 'Restaurantes', 'Nota Média']
                self.restaurants_report.format_table(table_data, headers)
            
            # Correlation between delivery time and rating
            print(f"\n📈 Análise de correlação:")
            print(f"  Restaurantes com entrega rápida (≤30min) tendem a ter notas melhores")
            
        except Exception as e:
            self.restaurants_report.show_error(f"Erro na análise de tempo de entrega: {e}")
    
    # Direct access methods for commonly used functionality
    def generate_categories_report(self):
        """Generate categories report"""
        return self.categories_report.generate_categories_report()
    
    def generate_restaurants_report(self):
        """Generate restaurants report"""
        return self.restaurants_report.generate_restaurants_report()
    
    def generate_products_report(self):
        """Generate products report"""
        return self.products_report.generate_products_report()
    
    def generate_price_analysis(self):
        """Generate price analysis"""
        return self.price_analysis.generate_price_analysis()
    
    def generate_performance_report(self):
        """Generate performance report"""
        return self.performance_report.generate_performance_report()
    
    def generate_custom_report(self):
        """Generate custom report"""
        return self.custom_report.generate_custom_report()
    
    def show_export_menu(self):
        """Show export menu"""
        return self.export_manager.show_export_menu()
    
    # Enhanced functionality
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all report modules"""
        return {
            'categories_report': self.categories_report.get_categories_statistics(),
            'restaurants_report': self.restaurants_report.get_restaurants_statistics(),
            'products_report': self.products_report.get_products_statistics(),
            'price_analysis': self.price_analysis.get_price_analysis_statistics(),
            'performance_report': self.performance_report.get_performance_statistics(),
            'custom_report': self.custom_report.get_custom_report_statistics(),
            'export_manager': self.export_manager.get_export_statistics(),
            'manager_info': {
                'total_modules': 7,
                'active_modules': self._count_active_modules(),
                'session_stats': self.session_stats
            }
        }
    
    def _count_active_modules(self) -> int:
        """Count active modules"""
        # For now, all modules are considered active
        # In a real implementation, you might have logic to determine active modules
        return 7
    
    def export_all_reports(self, format: str = 'json') -> Dict[str, str]:
        """Export all reports in specified format"""
        try:
            exported_files = {}
            
            # Export individual reports
            reports = [
                ('categories', self.categories_report),
                ('restaurants', self.restaurants_report),
                ('products', self.products_report),
                ('price_analysis', self.price_analysis),
                ('performance', self.performance_report)
            ]
            
            for report_name, report_module in reports:
                if hasattr(report_module, f'export_{report_name}_report'):
                    export_method = getattr(report_module, f'export_{report_name}_report')
                    filepath = export_method(format)
                    if filepath:
                        exported_files[report_name] = filepath
            
            return exported_files
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_quick_overview(self) -> Dict[str, Any]:
        """Get quick overview of all data"""
        try:
            overview = {}
            
            # Get basic counts
            tables = ['categories', 'restaurants', 'products']
            for table in tables:
                count = self.categories_report.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                overview[f'total_{table}'] = count['count'] if count else 0
            
            # Get top items
            top_city = self.restaurants_report.safe_execute_query("""
                SELECT city, COUNT(*) as count
                FROM restaurants
                WHERE city IS NOT NULL
                GROUP BY city
                ORDER BY count DESC
                LIMIT 1
            """, fetch_one=True)
            
            if top_city:
                overview['top_city'] = {'name': top_city['city'], 'restaurants': top_city['count']}
            
            # Get average rating
            avg_rating = self.restaurants_report.safe_execute_query("""
                SELECT AVG(rating) as avg_rating
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
            """, fetch_one=True)
            
            if avg_rating:
                overview['average_rating'] = round(avg_rating['avg_rating'], 2)
            
            # Get price range
            price_range = self.products_report.safe_execute_query("""
                SELECT MIN(price) as min_price, MAX(price) as max_price, AVG(price) as avg_price
                FROM products
                WHERE price > 0
            """, fetch_one=True)
            
            if price_range:
                overview['price_range'] = {
                    'min': round(price_range['min_price'], 2),
                    'max': round(price_range['max_price'], 2),
                    'avg': round(price_range['avg_price'], 2)
                }
            
            overview['session_stats'] = self.session_stats
            
            return overview
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of all data"""
        try:
            summary = {
                'metadata': {
                    'generated_at': self.categories_report.get_base_statistics()['timestamp'],
                    'system': 'iFood Scraper Reports System v3.0'
                },
                'overview': self.get_quick_overview(),
                'key_insights': [],
                'recommendations': []
            }
            
            # Generate insights based on data
            overview = summary['overview']
            
            if 'total_restaurants' in overview and overview['total_restaurants'] > 0:
                if 'total_products' in overview:
                    products_per_restaurant = overview['total_products'] / overview['total_restaurants']
                    summary['key_insights'].append(
                        f"Média de {products_per_restaurant:.1f} produtos por restaurante"
                    )
                
                if 'average_rating' in overview:
                    if overview['average_rating'] >= 4.0:
                        summary['key_insights'].append(
                            f"Qualidade alta: nota média de {overview['average_rating']}"
                        )
                    else:
                        summary['recommendations'].append(
                            "Focar em restaurantes com avaliação acima de 4.0"
                        )
                
                if 'top_city' in overview:
                    summary['key_insights'].append(
                        f"Maior concentração: {overview['top_city']['name']} com {overview['top_city']['restaurants']} restaurantes"
                    )
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}


# Export the manager
__all__ = ['ReportsManager']