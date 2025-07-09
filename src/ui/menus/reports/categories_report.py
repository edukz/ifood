#!/usr/bin/env python3
"""
Categories Report - Category analysis and statistics
"""

from typing import Dict, Any, List
from pathlib import Path

from .reports_base import ReportsBase


class CategoriesReport(ReportsBase):
    """Category analysis and statistics reporting"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatório de Categorias", session_stats, data_dir)
    
    def generate_categories_report(self):
        """Generate comprehensive categories report"""
        self.print_section_header("📊 RELATÓRIO DE CATEGORIAS")
        
        # Basic statistics
        self._show_basic_statistics()
        
        # Distribution by city
        self._show_city_distribution()
        
        # Most popular categories
        self._show_popular_categories()
        
        # Recently added categories
        self._show_recent_categories()
        
        # Category analysis
        self._show_category_analysis()
    
    def _show_basic_statistics(self):
        """Show basic category statistics"""
        try:
            total = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM categories WHERE is_active = TRUE",
                fetch_one=True
            )
            
            if total:
                print(f"📋 Total de categorias ativas: {total['total']}")
            
            # Active vs inactive
            inactive = self.safe_execute_query(
                "SELECT COUNT(*) as total FROM categories WHERE is_active = FALSE",
                fetch_one=True
            )
            
            if inactive:
                print(f"⏸️ Categorias inativas: {inactive['total']}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas básicas: {e}")
    
    def _show_city_distribution(self):
        """Show category distribution by city"""
        self.print_subsection_header("🌍 DISTRIBUIÇÃO POR CIDADE")
        
        try:
            query = """
                SELECT 
                    CASE 
                        WHEN url LIKE '%birigui%' THEN 'Birigui'
                        WHEN url LIKE '%aracatuba%' THEN 'Araçatuba'
                        WHEN url LIKE '%penapolis%' THEN 'Penápolis'
                        ELSE 'Outras'
                    END as cidade,
                    COUNT(*) as total
                FROM categories 
                WHERE is_active = TRUE
                GROUP BY cidade
                ORDER BY total DESC
            """
            
            cities = self.safe_execute_query(query)
            
            if cities:
                table_data = []
                for city in cities:
                    table_data.append([city['cidade'], city['total']])
                
                headers = ['Cidade', 'Categorias']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de distribuição por cidade encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter distribuição por cidade: {e}")
    
    def _show_popular_categories(self):
        """Show most popular categories by restaurant count"""
        self.print_subsection_header("🏆 TOP 15 CATEGORIAS MAIS POPULARES")
        
        try:
            query = """
                SELECT c.name, COUNT(r.id) as restaurant_count
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                WHERE c.is_active = TRUE
                GROUP BY c.id, c.name
                ORDER BY restaurant_count DESC
                LIMIT 15
            """
            
            popular = self.safe_execute_query(query)
            
            if popular:
                table_data = []
                for i, cat in enumerate(popular, 1):
                    table_data.append([i, cat['name'], cat['restaurant_count']])
                
                headers = ['Pos', 'Categoria', 'Restaurantes']
                self.format_table(table_data, headers)
            else:
                print("Nenhum dado de popularidade encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter categorias populares: {e}")
    
    def _show_recent_categories(self):
        """Show recently added categories"""
        self.print_subsection_header("🆕 CATEGORIAS ADICIONADAS NA ÚLTIMA SEMANA")
        
        try:
            query = """
                SELECT name, created_at
                FROM categories 
                WHERE is_active = TRUE 
                  AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
                ORDER BY created_at DESC
                LIMIT 10
            """
            
            recent = self.safe_execute_query(query)
            
            if recent:
                table_data = []
                for cat in recent:
                    table_data.append([
                        cat['name'],
                        self.format_date(cat['created_at'])
                    ])
                
                headers = ['Categoria', 'Data/Hora']
                self.format_table(table_data, headers)
            else:
                print("Nenhuma categoria adicionada na última semana")
                
        except Exception as e:
            self.show_error(f"Erro ao obter categorias recentes: {e}")
    
    def _show_category_analysis(self):
        """Show detailed category analysis"""
        self.print_subsection_header("📈 ANÁLISE DETALHADA")
        
        try:
            # Categories with no restaurants
            empty_categories = self.safe_execute_query("""
                SELECT c.name
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                WHERE c.is_active = TRUE AND r.id IS NULL
                LIMIT 10
            """)
            
            if empty_categories:
                print(f"📭 Categorias sem restaurantes ({len(empty_categories)}):")
                for cat in empty_categories[:5]:  # Show only first 5
                    print(f"  • {cat['name']}")
                if len(empty_categories) > 5:
                    print(f"  ... e mais {len(empty_categories) - 5}")
            
            # Category name analysis
            self._analyze_category_names()
            
        except Exception as e:
            self.show_error(f"Erro na análise detalhada: {e}")
    
    def _analyze_category_names(self):
        """Analyze category name patterns"""
        try:
            # Most common words in category names
            query = """
                SELECT name
                FROM categories 
                WHERE is_active = TRUE
            """
            
            categories = self.safe_execute_query(query)
            
            if categories:
                # Simple word frequency analysis
                word_count = {}
                for cat in categories:
                    name = cat['name'].lower()
                    words = name.replace('-', ' ').replace('_', ' ').split()
                    for word in words:
                        if len(word) > 3:  # Only words longer than 3 chars
                            word_count[word] = word_count.get(word, 0) + 1
                
                # Top words
                top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
                
                if top_words:
                    print(f"\n🔤 Palavras mais comuns nos nomes:")
                    table_data = []
                    for word, count in top_words:
                        table_data.append([word.title(), count])
                    
                    headers = ['Palavra', 'Frequência']
                    self.format_table(table_data, headers)
                    
        except Exception as e:
            self.show_error(f"Erro na análise de nomes: {e}")
    
    def export_categories_report(self, format: str = 'csv') -> str:
        """
        Export categories report data
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Get all category data
            query = """
                SELECT 
                    c.name,
                    c.url,
                    c.is_active,
                    c.created_at,
                    COUNT(r.id) as restaurant_count,
                    CASE 
                        WHEN c.url LIKE '%birigui%' THEN 'Birigui'
                        WHEN c.url LIKE '%aracatuba%' THEN 'Araçatuba'
                        WHEN c.url LIKE '%penapolis%' THEN 'Penápolis'
                        ELSE 'Outras'
                    END as cidade
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                GROUP BY c.id, c.name, c.url, c.is_active, c.created_at
                ORDER BY restaurant_count DESC, c.name
            """
            
            categories = self.safe_execute_query(query)
            
            if not categories:
                raise ValueError("Nenhum dado de categoria encontrado")
            
            # Convert to list of dicts
            data = [dict(cat) for cat in categories]
            
            if format.lower() == 'json':
                # Create comprehensive JSON report
                report_data = {
                    'metadata': self.get_base_statistics(),
                    'summary': {
                        'total_categories': len(data),
                        'active_categories': sum(1 for cat in data if cat['is_active']),
                        'categories_with_restaurants': sum(1 for cat in data if cat['restaurant_count'] > 0)
                    },
                    'categories': data
                }
                filepath = self.export_to_json(report_data, 'categorias_relatorio')
            else:
                # Export as CSV
                fieldnames = ['name', 'url', 'is_active', 'created_at', 'restaurant_count', 'cidade']
                filepath = self.export_to_csv(data, 'categorias_relatorio', fieldnames)
            
            return str(filepath)
            
        except Exception as e:
            self.show_error(f"Erro ao exportar relatório: {e}")
            return ""
    
    def get_categories_statistics(self) -> Dict[str, Any]:
        """Get categories report statistics"""
        stats = self.get_base_statistics()
        
        try:
            # Basic counts
            total_active = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM categories WHERE is_active = TRUE",
                fetch_one=True
            )
            
            total_inactive = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM categories WHERE is_active = FALSE", 
                fetch_one=True
            )
            
            # Categories with restaurants
            with_restaurants = self.safe_execute_query("""
                SELECT COUNT(DISTINCT c.id) as count
                FROM categories c
                JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                WHERE c.is_active = TRUE
            """, fetch_one=True)
            
            stats['categories_stats'] = {
                'total_active': total_active['count'] if total_active else 0,
                'total_inactive': total_inactive['count'] if total_inactive else 0,
                'with_restaurants': with_restaurants['count'] if with_restaurants else 0
            }
            
            # Recent activity
            recent_data = self.get_date_range_data('categories', 'created_at', 7)
            stats['recent_activity'] = recent_data
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats