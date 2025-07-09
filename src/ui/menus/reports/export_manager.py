#!/usr/bin/env python3
"""
Export Manager - Data export and format management
"""

import json
import csv
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .reports_base import ReportsBase


class ExportManager(ReportsBase):
    """Data export and format management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Gerenciador de Exportação", session_stats, data_dir)
    
    def show_export_menu(self):
        """Show export data menu"""
        self.print_section_header("📁 EXPORTAR DADOS")
        
        export_options = [
            "1. 📊 Exportar restaurantes (CSV)",
            "2. 🍕 Exportar produtos (CSV)",
            "3. 🏷️ Exportar categorias (CSV)",
            "4. 📋 Exportar relatório completo (JSON)",
            "5. 🎯 Exportar dados personalizados",
            "6. 📦 Exportar tudo (pacote completo)"
        ]
        
        for option in export_options:
            print(f"  {option}")
        
        choice = input("\nEscolha uma opção (1-6): ").strip()
        
        if choice == "1":
            self.export_restaurants()
        elif choice == "2":
            self.export_products()
        elif choice == "3":
            self.export_categories()
        elif choice == "4":
            self.export_full_report()
        elif choice == "5":
            self.export_custom_data()
        elif choice == "6":
            self.export_complete_package()
        else:
            print("❌ Opção inválida")
    
    def export_restaurants(self):
        """Export restaurants to CSV"""
        try:
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
            
            if restaurants:
                # Convert to list of dicts
                data = [dict(rest) for rest in restaurants]
                
                fieldnames = ['name', 'category', 'rating', 'delivery_time', 'delivery_fee',
                            'distance', 'city', 'address', 'created_at', 'product_count']
                
                filepath = self.export_to_csv(data, 'restaurantes_export', fieldnames)
                print(f"✅ Exportado {len(restaurants)} restaurantes para {filepath}")
            else:
                print("❌ Nenhum restaurante encontrado para exportar")
                
        except Exception as e:
            self.show_error(f"Erro ao exportar restaurantes: {e}")
    
    def export_products(self):
        """Export products to CSV"""
        try:
            query = """
                SELECT 
                    p.name, 
                    p.price, 
                    p.category, 
                    p.description,
                    r.name as restaurant_name, 
                    r.category as restaurant_category,
                    r.city as restaurant_city,
                    p.created_at
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                ORDER BY p.name
            """
            
            products = self.safe_execute_query(query)
            
            if products:
                # Convert to list of dicts
                data = [dict(prod) for prod in products]
                
                fieldnames = ['name', 'price', 'category', 'description',
                            'restaurant_name', 'restaurant_category', 
                            'restaurant_city', 'created_at']
                
                filepath = self.export_to_csv(data, 'produtos_export', fieldnames)
                print(f"✅ Exportado {len(products)} produtos para {filepath}")
            else:
                print("❌ Nenhum produto encontrado para exportar")
                
        except Exception as e:
            self.show_error(f"Erro ao exportar produtos: {e}")
    
    def export_categories(self):
        """Export categories to CSV"""
        try:
            query = """
                SELECT 
                    c.name, 
                    c.url, 
                    c.is_active, 
                    c.created_at,
                    COUNT(r.id) as restaurant_count
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                GROUP BY c.id, c.name, c.url, c.is_active, c.created_at
                ORDER BY c.name
            """
            
            categories = self.safe_execute_query(query)
            
            if categories:
                # Convert to list of dicts
                data = [dict(cat) for cat in categories]
                
                fieldnames = ['name', 'url', 'is_active', 'created_at', 'restaurant_count']
                
                filepath = self.export_to_csv(data, 'categorias_export', fieldnames)
                print(f"✅ Exportado {len(categories)} categorias para {filepath}")
            else:
                print("❌ Nenhuma categoria encontrada para exportar")
                
        except Exception as e:
            self.show_error(f"Erro ao exportar categorias: {e}")
    
    def export_full_report(self):
        """Export comprehensive report in JSON"""
        try:
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'system': 'iFood Scraper Report System',
                    'version': '3.0',
                    'session_stats': self.session_stats
                },
                'statistics': {},
                'data': {},
                'analysis': {}
            }
            
            # Basic statistics
            tables_stats = {}
            for table in ['restaurants', 'products', 'categories']:
                count = self.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                tables_stats[f'total_{table}'] = count['count'] if count else 0
            
            report['statistics'] = tables_stats
            
            # Top data
            self._add_top_data_to_report(report)
            
            # Analysis data
            self._add_analysis_data_to_report(report)
            
            # Export to JSON
            filepath = self.export_to_json(report, 'relatorio_completo')
            print(f"✅ Relatório completo exportado para {filepath}")
            
        except Exception as e:
            self.show_error(f"Erro ao exportar relatório completo: {e}")
    
    def _add_top_data_to_report(self, report: Dict[str, Any]):
        """Add top data to the report"""
        try:
            # Top categories by restaurant count
            top_categories = self.safe_execute_query("""
                SELECT category, COUNT(*) as count
                FROM restaurants
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
            
            if top_categories:
                report['data']['top_categories'] = [dict(row) for row in top_categories]
            
            # Top cities by restaurant count
            top_cities = self.safe_execute_query("""
                SELECT city, COUNT(*) as count
                FROM restaurants
                WHERE city IS NOT NULL
                GROUP BY city
                ORDER BY count DESC
                LIMIT 10
            """)
            
            if top_cities:
                report['data']['top_cities'] = [dict(row) for row in top_cities]
            
            # Top rated restaurants
            top_rated = self.safe_execute_query("""
                SELECT name, category, rating, city
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
                ORDER BY rating DESC, name ASC
                LIMIT 10
            """)
            
            if top_rated:
                report['data']['top_rated_restaurants'] = [dict(row) for row in top_rated]
                
        except Exception as e:
            self.show_error(f"Erro ao adicionar top data: {e}")
    
    def _add_analysis_data_to_report(self, report: Dict[str, Any]):
        """Add analysis data to the report"""
        try:
            # Price analysis
            price_analysis = self.safe_execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price
                FROM products
                WHERE price > 0
            """, fetch_one=True)
            
            if price_analysis:
                report['analysis']['price_analysis'] = dict(price_analysis)
            
            # Rating distribution
            rating_distribution = self.safe_execute_query("""
                SELECT 
                    CASE 
                        WHEN rating >= 4.5 THEN 'Excelente'
                        WHEN rating >= 4.0 THEN 'Muito Bom'
                        WHEN rating >= 3.5 THEN 'Bom'
                        WHEN rating >= 3.0 THEN 'Regular'
                        ELSE 'Ruim'
                    END as rating_category,
                    COUNT(*) as count
                FROM restaurants
                WHERE rating IS NOT NULL AND rating > 0
                GROUP BY rating_category
                ORDER BY MIN(rating) DESC
            """)
            
            if rating_distribution:
                report['analysis']['rating_distribution'] = [dict(row) for row in rating_distribution]
            
            # Growth data (last 30 days)
            growth_data = self.safe_execute_query("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as restaurants_added
                FROM restaurants
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            if growth_data:
                report['analysis']['growth_last_30_days'] = [dict(row) for row in growth_data]
                
        except Exception as e:
            self.show_error(f"Erro ao adicionar análise: {e}")
    
    def export_custom_data(self):
        """Export custom filtered data"""
        self.print_subsection_header("🎯 EXPORTAÇÃO PERSONALIZADA")
        
        # Get table selection
        table = input("Tabela (restaurants/products/categories): ").strip().lower()
        if table not in ['restaurants', 'products', 'categories']:
            self.show_error("Tabela inválida!")
            return
        
        # Get filters
        filters = self._get_export_filters(table)
        
        # Get format
        format_choice = input("Formato (csv/json) [csv]: ").strip().lower() or "csv"
        
        # Get limit
        limit = input("Limite de registros [1000]: ").strip() or "1000"
        try:
            limit = int(limit)
            if limit < 1 or limit > 50000:
                raise ValueError("Limite deve estar entre 1 e 50000")
        except ValueError:
            self.show_error("Limite inválido. Usando 1000.")
            limit = 1000
        
        try:
            # Build query
            query, params = self._build_export_query(table, filters, limit)
            
            # Execute query
            results = self.safe_execute_query(query, tuple(params))
            
            if results:
                # Convert to list of dicts
                data = [dict(row) for row in results]
                
                # Create filename with filter info
                filter_summary = "_".join([f"{k}_{v}" for k, v in filters.items() if len(str(v)) < 10])[:30]
                filename = f"{table}_personalizado_{filter_summary}" if filter_summary else f"{table}_personalizado"
                
                if format_choice == 'json':
                    # Add metadata for JSON
                    export_data = {
                        'metadata': {
                            'table': table,
                            'filters': filters,
                            'total_results': len(data),
                            'generated_at': datetime.now().isoformat()
                        },
                        'data': data
                    }
                    filepath = self.export_to_json(export_data, filename)
                else:
                    # Export as CSV
                    fieldnames = list(data[0].keys()) if data else []
                    filepath = self.export_to_csv(data, filename, fieldnames)
                
                print(f"✅ Exportado {len(results)} registros para {filepath}")
            else:
                print("❌ Nenhum resultado encontrado com os filtros especificados")
                
        except Exception as e:
            self.show_error(f"Erro na exportação personalizada: {e}")
    
    def _get_export_filters(self, table: str) -> Dict[str, str]:
        """Get export filters for a specific table"""
        filters = {}
        
        if table == 'restaurants':
            filters['city'] = input("Cidade (opcional): ").strip()
            filters['category'] = input("Categoria (opcional): ").strip()
            filters['min_rating'] = input("Avaliação mínima (opcional): ").strip()
        elif table == 'products':
            filters['category'] = input("Categoria do produto (opcional): ").strip()
            filters['max_price'] = input("Preço máximo (opcional): ").strip()
            filters['restaurant_city'] = input("Cidade do restaurante (opcional): ").strip()
        elif table == 'categories':
            filters['active_only'] = input("Apenas ativas? (s/n) [s]: ").strip() or 's'
            filters['name_pattern'] = input("Padrão no nome (opcional): ").strip()
        
        # Remove empty filters
        return {k: v for k, v in filters.items() if v}
    
    def _build_export_query(self, table: str, filters: Dict[str, str], limit: int) -> tuple:
        """Build export query with filters"""
        params = []
        
        if table == 'restaurants':
            query = """
                SELECT r.*, COUNT(p.id) as product_count
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
            """
            
            conditions = []
            if 'city' in filters:
                conditions.append("r.city LIKE %s")
                params.append(f"%{filters['city']}%")
            
            if 'category' in filters:
                conditions.append("r.category LIKE %s")
                params.append(f"%{filters['category']}%")
            
            if 'min_rating' in filters:
                try:
                    min_rating = float(filters['min_rating'])
                    conditions.append("r.rating >= %s")
                    params.append(min_rating)
                except ValueError:
                    pass
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY r.id"
            query += f" ORDER BY r.name LIMIT {limit}"
            
        elif table == 'products':
            query = """
                SELECT p.*, r.name as restaurant_name, r.city as restaurant_city
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
            """
            
            conditions = []
            if 'category' in filters:
                conditions.append("p.category LIKE %s")
                params.append(f"%{filters['category']}%")
            
            if 'max_price' in filters:
                try:
                    max_price = float(filters['max_price'])
                    conditions.append("p.price <= %s")
                    params.append(max_price)
                except ValueError:
                    pass
            
            if 'restaurant_city' in filters:
                conditions.append("r.city LIKE %s")
                params.append(f"%{filters['restaurant_city']}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += f" ORDER BY p.name LIMIT {limit}"
            
        else:  # categories
            query = """
                SELECT c.*, COUNT(r.id) as restaurant_count
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
            """
            
            conditions = []
            if filters.get('active_only', 's').lower() == 's':
                conditions.append("c.is_active = TRUE")
            
            if 'name_pattern' in filters:
                conditions.append("c.name LIKE %s")
                params.append(f"%{filters['name_pattern']}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY c.id"
            query += f" ORDER BY c.name LIMIT {limit}"
        
        return query, params
    
    def export_complete_package(self):
        """Export complete data package"""
        self.print_subsection_header("📦 EXPORTAÇÃO COMPLETA")
        
        try:
            print("Criando pacote completo de exportação...")
            
            # Create package directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            package_dir = self.data_dir / f"pacote_completo_{timestamp}"
            package_dir.mkdir(exist_ok=True)
            
            exported_files = []
            
            # Export each table
            tables_info = [
                ('restaurants', 'restaurantes'),
                ('products', 'produtos'),
                ('categories', 'categorias')
            ]
            
            for table, label in tables_info:
                print(f"  Exportando {label}...")
                
                if table == 'restaurants':
                    query = """
                        SELECT r.*, COUNT(p.id) as product_count
                        FROM restaurants r
                        LEFT JOIN products p ON p.restaurant_id = r.id
                        GROUP BY r.id
                        ORDER BY r.name
                    """
                elif table == 'products':
                    query = """
                        SELECT p.*, r.name as restaurant_name, r.city as restaurant_city
                        FROM products p
                        JOIN restaurants r ON p.restaurant_id = r.id
                        ORDER BY p.name
                    """
                else:  # categories
                    query = """
                        SELECT c.*, COUNT(r.id) as restaurant_count
                        FROM categories c
                        LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                        GROUP BY c.id
                        ORDER BY c.name
                    """
                
                data = self.safe_execute_query(query)
                
                if data:
                    # Export as CSV
                    csv_filename = f"{label}.csv"
                    csv_filepath = package_dir / csv_filename
                    
                    with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                        if data:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            for row in data:
                                writer.writerow(dict(row))
                    
                    exported_files.append(csv_filename)
                    print(f"    ✅ {label}: {len(data)} registros")
            
            # Create summary report
            summary_data = {
                'package_info': {
                    'created_at': datetime.now().isoformat(),
                    'total_files': len(exported_files),
                    'files': exported_files
                },
                'statistics': {},
                'session_info': self.session_stats
            }
            
            # Add statistics
            for table in ['restaurants', 'products', 'categories']:
                count = self.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                summary_data['statistics'][table] = count['count'] if count else 0
            
            # Export summary as JSON
            summary_filepath = package_dir / "resumo_exportacao.json"
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Pacote completo criado em: {package_dir}")
            print(f"📁 Arquivos incluídos: {len(exported_files) + 1}")
            for file in exported_files + ['resumo_exportacao.json']:
                print(f"    • {file}")
            
        except Exception as e:
            self.show_error(f"Erro ao criar pacote completo: {e}")
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export manager statistics"""
        stats = self.get_base_statistics()
        
        # Add export capabilities info
        stats['export_capabilities'] = {
            'supported_formats': ['csv', 'json'],
            'supported_tables': ['restaurants', 'products', 'categories'],
            'max_records_per_export': 50000,
            'available_filters': {
                'restaurants': ['city', 'category', 'min_rating'],
                'products': ['category', 'max_price', 'restaurant_city'],
                'categories': ['active_only', 'name_pattern']
            }
        }
        
        # Add current data volume
        try:
            for table in ['restaurants', 'products', 'categories']:
                count = self.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                stats[f'available_{table}'] = count['count'] if count else 0
        except Exception as e:
            stats['error'] = str(e)
        
        return stats