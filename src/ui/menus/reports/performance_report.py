#!/usr/bin/env python3
"""
Performance Report - System performance and growth statistics
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from .reports_base import ReportsBase


class PerformanceReport(ReportsBase):
    """System performance and growth statistics reporting"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatório de Performance", session_stats, data_dir)
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        self.print_section_header("🎯 RELATÓRIO DE PERFORMANCE")
        
        # Session statistics
        self._show_session_statistics()
        
        # Database statistics
        self._show_database_statistics()
        
        # Growth analysis
        self._show_growth_analysis()
        
        # Efficiency metrics
        self._show_efficiency_metrics()
        
        # System health indicators
        self._show_system_health()
    
    def _show_session_statistics(self):
        """Show current session statistics"""
        self.print_subsection_header("📊 ESTATÍSTICAS DA SESSÃO ATUAL")
        
        try:
            print(f"  🏷️ Categorias extraídas: {self.session_stats.get('categories_extracted', 0):,}")
            print(f"  🏪 Restaurantes extraídos: {self.session_stats.get('restaurants_extracted', 0):,}")
            print(f"  🍕 Produtos extraídos: {self.session_stats.get('products_extracted', 0):,}")
            print(f"  ❌ Erros encontrados: {self.session_stats.get('errors', 0):,}")
            
            execution_time = self.session_stats.get('execution_time', 0)
            print(f"  ⏱️ Tempo de execução: {execution_time:.2f}s")
            
            # Calculate throughput
            total_extracted = (
                self.session_stats.get('categories_extracted', 0) +
                self.session_stats.get('restaurants_extracted', 0) +
                self.session_stats.get('products_extracted', 0)
            )
            
            if execution_time > 0 and total_extracted > 0:
                throughput = total_extracted / execution_time
                print(f"  ⚡ Throughput: {throughput:.2f} itens/segundo")
            
            # Session duration
            session_start = self.session_stats.get('session_start')
            if session_start:
                if isinstance(session_start, str):
                    session_start = datetime.fromisoformat(session_start)
                
                duration = datetime.now() - session_start
                print(f"  🕐 Duração da sessão: {self._format_duration(duration.total_seconds())}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas da sessão: {e}")
    
    def _show_database_statistics(self):
        """Show database statistics"""
        self.print_subsection_header("📋 ESTATÍSTICAS DO BANCO DE DADOS")
        
        try:
            # Table counts
            tables_data = [
                ('categories', 'Categorias'),
                ('restaurants', 'Restaurantes'),
                ('products', 'Produtos')
            ]
            
            table_stats = []
            for table, label in tables_data:
                count = self.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                
                if count:
                    table_stats.append([label, f"{count['count']:,}"])
            
            if table_stats:
                headers = ['Tabela', 'Registros']
                self.format_table(table_stats, headers)
            
            # Success rate calculation
            restaurants_count = self.safe_execute_query(
                "SELECT COUNT(*) as count FROM restaurants",
                fetch_one=True
            )
            
            restaurants_with_products = self.safe_execute_query(
                "SELECT COUNT(DISTINCT restaurant_id) as count FROM products",
                fetch_one=True
            )
            
            if restaurants_count and restaurants_with_products and restaurants_count['count'] > 0:
                success_rate = (restaurants_with_products['count'] / restaurants_count['count']) * 100
                print(f"\n  ✅ Taxa de sucesso (restaurantes com produtos): {success_rate:.1f}%")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas do banco: {e}")
    
    def _show_growth_analysis(self):
        """Show growth analysis over time"""
        self.print_subsection_header("📈 ANÁLISE DE CRESCIMENTO")
        
        try:
            # Growth in last 7 days
            periods = [1, 3, 7, 30]  # days
            
            for days in periods:
                growth_data = []
                
                for table, label in [('restaurants', 'Restaurantes'), ('products', 'Produtos')]:
                    count = self.safe_execute_query(f"""
                        SELECT COUNT(*) as count
                        FROM {table}
                        WHERE created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
                    """, fetch_one=True)
                    
                    if count:
                        growth_data.append([label, count['count']])
                
                if growth_data and any(row[1] > 0 for row in growth_data):
                    print(f"\n📅 Últimos {days} dia(s):")
                    headers = ['Tipo', 'Adicionados']
                    self.format_table(growth_data, headers)
            
            # Daily growth trend
            self._show_daily_growth_trend()
            
        except Exception as e:
            self.show_error(f"Erro na análise de crescimento: {e}")
    
    def _show_daily_growth_trend(self):
        """Show daily growth trend"""
        try:
            daily_growth = self.safe_execute_query("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM restaurants
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            if daily_growth:
                print(f"\n📊 Crescimento diário de restaurantes (últimos 7 dias):")
                table_data = []
                for day in daily_growth:
                    table_data.append([
                        self.format_date(day['date']) if hasattr(day['date'], 'strftime') else str(day['date']),
                        day['count']
                    ])
                
                headers = ['Data', 'Restaurantes Adicionados']
                self.format_table(table_data, headers)
                
                # Calculate average daily growth
                if len(daily_growth) > 1:
                    avg_daily = sum(day['count'] for day in daily_growth) / len(daily_growth)
                    print(f"  📈 Média diária: {avg_daily:.1f} restaurantes/dia")
                    
        except Exception as e:
            self.show_error(f"Erro na tendência diária: {e}")
    
    def _show_efficiency_metrics(self):
        """Show system efficiency metrics"""
        self.print_subsection_header("⚡ MÉTRICAS DE EFICIÊNCIA")
        
        try:
            # Data quality metrics
            self._calculate_data_quality_metrics()
            
            # Performance benchmarks
            self._show_performance_benchmarks()
            
        except Exception as e:
            self.show_error(f"Erro nas métricas de eficiência: {e}")
    
    def _calculate_data_quality_metrics(self):
        """Calculate data quality metrics"""
        try:
            # Restaurant data completeness
            restaurant_metrics = self.safe_execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN rating IS NOT NULL AND rating > 0 THEN 1 ELSE 0 END) as with_rating,
                    SUM(CASE WHEN delivery_time IS NOT NULL THEN 1 ELSE 0 END) as with_delivery_time,
                    SUM(CASE WHEN delivery_fee IS NOT NULL THEN 1 ELSE 0 END) as with_delivery_fee,
                    SUM(CASE WHEN city IS NOT NULL THEN 1 ELSE 0 END) as with_city,
                    SUM(CASE WHEN category IS NOT NULL THEN 1 ELSE 0 END) as with_category
                FROM restaurants
            """, fetch_one=True)
            
            if restaurant_metrics and restaurant_metrics['total'] > 0:
                total = restaurant_metrics['total']
                print(f"📊 Qualidade dos dados de restaurantes:")
                print(f"  Com avaliação: {self.format_percentage((restaurant_metrics['with_rating'] / total) * 100)}")
                print(f"  Com tempo de entrega: {self.format_percentage((restaurant_metrics['with_delivery_time'] / total) * 100)}")
                print(f"  Com taxa de entrega: {self.format_percentage((restaurant_metrics['with_delivery_fee'] / total) * 100)}")
                print(f"  Com cidade: {self.format_percentage((restaurant_metrics['with_city'] / total) * 100)}")
                print(f"  Com categoria: {self.format_percentage((restaurant_metrics['with_category'] / total) * 100)}")
            
            # Product data completeness
            product_metrics = self.safe_execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN price IS NOT NULL AND price > 0 THEN 1 ELSE 0 END) as with_price,
                    SUM(CASE WHEN category IS NOT NULL THEN 1 ELSE 0 END) as with_category,
                    SUM(CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END) as with_description
                FROM products
            """, fetch_one=True)
            
            if product_metrics and product_metrics['total'] > 0:
                total = product_metrics['total']
                print(f"\n📊 Qualidade dos dados de produtos:")
                print(f"  Com preço: {self.format_percentage((product_metrics['with_price'] / total) * 100)}")
                print(f"  Com categoria: {self.format_percentage((product_metrics['with_category'] / total) * 100)}")
                print(f"  Com descrição: {self.format_percentage((product_metrics['with_description'] / total) * 100)}")
                
        except Exception as e:
            self.show_error(f"Erro nas métricas de qualidade: {e}")
    
    def _show_performance_benchmarks(self):
        """Show performance benchmarks"""
        try:
            print(f"\n🎯 Benchmarks de Performance:")
            
            # Extraction efficiency
            total_extracted = (
                self.session_stats.get('categories_extracted', 0) +
                self.session_stats.get('restaurants_extracted', 0) +
                self.session_stats.get('products_extracted', 0)
            )
            
            execution_time = self.session_stats.get('execution_time', 0)
            
            if execution_time > 0:
                throughput = total_extracted / execution_time
                
                # Define benchmarks
                benchmarks = {
                    'Throughput atual': (throughput, 'itens/segundo'),
                    'Meta mínima': (1.0, 'itens/segundo'),
                    'Meta ideal': (2.5, 'itens/segundo'),
                    'Meta otimizada': (5.0, 'itens/segundo')
                }
                
                table_data = []
                for metric, (value, unit) in benchmarks.items():
                    if metric == 'Throughput atual':
                        status = '🟢' if value >= 2.5 else '🟡' if value >= 1.0 else '🔴'
                    else:
                        status = '🎯'
                    
                    table_data.append([metric, f"{value:.2f}", unit, status])
                
                headers = ['Métrica', 'Valor', 'Unidade', 'Status']
                self.format_table(table_data, headers)
            
            # Error rate
            errors = self.session_stats.get('errors', 0)
            if total_extracted > 0:
                error_rate = (errors / (total_extracted + errors)) * 100
                print(f"\n📊 Taxa de erro: {self.format_percentage(error_rate)}")
                
                if error_rate < 5:
                    print(f"  🟢 Excelente (< 5%)")
                elif error_rate < 10:
                    print(f"  🟡 Aceitável (5-10%)")
                else:
                    print(f"  🔴 Precisa melhorar (> 10%)")
                    
        except Exception as e:
            self.show_error(f"Erro nos benchmarks: {e}")
    
    def _show_system_health(self):
        """Show system health indicators"""
        self.print_subsection_header("🏥 INDICADORES DE SAÚDE DO SISTEMA")
        
        try:
            health_indicators = []
            
            # Database connectivity
            try:
                with self.db.get_cursor() as (cursor, _):
                    cursor.execute("SELECT 1")
                    health_indicators.append(['Conectividade DB', '🟢', 'Online'])
            except Exception:
                health_indicators.append(['Conectividade DB', '🔴', 'Offline'])
            
            # Data freshness
            latest_restaurant = self.safe_execute_query(
                "SELECT MAX(created_at) as latest FROM restaurants",
                fetch_one=True
            )
            
            if latest_restaurant and latest_restaurant['latest']:
                latest_time = latest_restaurant['latest']
                if isinstance(latest_time, str):
                    latest_time = datetime.fromisoformat(latest_time)
                
                time_diff = datetime.now() - latest_time
                
                if time_diff.days < 1:
                    health_indicators.append(['Dados Recentes', '🟢', '< 24h'])
                elif time_diff.days < 7:
                    health_indicators.append(['Dados Recentes', '🟡', f'{time_diff.days} dias'])
                else:
                    health_indicators.append(['Dados Recentes', '🔴', f'{time_diff.days} dias'])
            
            # Data volume
            total_records = 0
            for table in ['categories', 'restaurants', 'products']:
                count = self.safe_execute_query(
                    f"SELECT COUNT(*) as count FROM {table}",
                    fetch_one=True
                )
                if count:
                    total_records += count['count']
            
            if total_records > 10000:
                health_indicators.append(['Volume de Dados', '🟢', f'{total_records:,} registros'])
            elif total_records > 1000:
                health_indicators.append(['Volume de Dados', '🟡', f'{total_records:,} registros'])
            else:
                health_indicators.append(['Volume de Dados', '🔴', f'{total_records:,} registros'])
            
            # Session performance
            execution_time = self.session_stats.get('execution_time', 0)
            if execution_time > 0:
                total_extracted = (
                    self.session_stats.get('categories_extracted', 0) +
                    self.session_stats.get('restaurants_extracted', 0) +
                    self.session_stats.get('products_extracted', 0)
                )
                
                if total_extracted > 0:
                    throughput = total_extracted / execution_time
                    
                    if throughput >= 2.5:
                        health_indicators.append(['Performance', '🟢', f'{throughput:.2f} itens/s'])
                    elif throughput >= 1.0:
                        health_indicators.append(['Performance', '🟡', f'{throughput:.2f} itens/s'])
                    else:
                        health_indicators.append(['Performance', '🔴', f'{throughput:.2f} itens/s'])
            
            if health_indicators:
                headers = ['Indicador', 'Status', 'Valor']
                self.format_table(health_indicators, headers)
                
                # Overall health score
                green_count = sum(1 for indicator in health_indicators if '🟢' in indicator[1])
                total_indicators = len(health_indicators)
                health_score = (green_count / total_indicators) * 100
                
                print(f"\n🎯 Score de Saúde Geral: {health_score:.1f}%")
                
                if health_score >= 90:
                    print(f"  🟢 Sistema em excelente estado")
                elif health_score >= 75:
                    print(f"  🟡 Sistema em bom estado")
                else:
                    print(f"  🔴 Sistema precisa de atenção")
                    
        except Exception as e:
            self.show_error(f"Erro nos indicadores de saúde: {e}")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def export_performance_report(self, format: str = 'csv') -> str:
        """
        Export performance report data
        
        Args:
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Collect all performance data
            performance_data = {
                'metadata': self.get_base_statistics(),
                'session_stats': self.session_stats,
                'database_stats': self._get_database_stats(),
                'growth_stats': self._get_growth_stats(),
                'efficiency_metrics': self._get_efficiency_metrics(),
                'health_indicators': self._get_health_indicators()
            }
            
            if format.lower() == 'json':
                filepath = self.export_to_json(performance_data, 'performance_relatorio')
            else:
                # Convert to flat structure for CSV
                flat_data = []
                
                # Session statistics
                session_row = {
                    'metric_type': 'session',
                    'metric_name': 'current_session',
                    'categories_extracted': self.session_stats.get('categories_extracted', 0),
                    'restaurants_extracted': self.session_stats.get('restaurants_extracted', 0),
                    'products_extracted': self.session_stats.get('products_extracted', 0),
                    'execution_time': self.session_stats.get('execution_time', 0),
                    'errors': self.session_stats.get('errors', 0)
                }
                flat_data.append(session_row)
                
                # Database statistics
                db_stats = performance_data['database_stats']
                for table, count in db_stats.items():
                    if table.endswith('_count'):
                        flat_data.append({
                            'metric_type': 'database',
                            'metric_name': table,
                            'value': count,
                            'categories_extracted': 0,
                            'restaurants_extracted': 0,
                            'products_extracted': 0,
                            'execution_time': 0,
                            'errors': 0
                        })
                
                fieldnames = ['metric_type', 'metric_name', 'value', 'categories_extracted', 
                            'restaurants_extracted', 'products_extracted', 'execution_time', 'errors']
                filepath = self.export_to_csv(flat_data, 'performance_relatorio', fieldnames)
            
            return str(filepath)
            
        except Exception as e:
            self.show_error(f"Erro ao exportar relatório: {e}")
            return ""
    
    def _get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        
        for table in ['categories', 'restaurants', 'products']:
            count = self.safe_execute_query(
                f"SELECT COUNT(*) as count FROM {table}",
                fetch_one=True
            )
            stats[f'{table}_count'] = count['count'] if count else 0
        
        return stats
    
    def _get_growth_stats(self) -> Dict[str, Any]:
        """Get growth statistics"""
        stats = {}
        
        for days in [1, 7, 30]:
            for table in ['restaurants', 'products']:
                count = self.safe_execute_query(f"""
                    SELECT COUNT(*) as count
                    FROM {table}
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
                """, fetch_one=True)
                
                stats[f'{table}_last_{days}_days'] = count['count'] if count else 0
        
        return stats
    
    def _get_efficiency_metrics(self) -> Dict[str, float]:
        """Get efficiency metrics"""
        metrics = {}
        
        # Session efficiency
        total_extracted = (
            self.session_stats.get('categories_extracted', 0) +
            self.session_stats.get('restaurants_extracted', 0) +
            self.session_stats.get('products_extracted', 0)
        )
        
        execution_time = self.session_stats.get('execution_time', 0)
        errors = self.session_stats.get('errors', 0)
        
        if execution_time > 0:
            metrics['throughput'] = total_extracted / execution_time
        
        if total_extracted > 0:
            metrics['error_rate'] = (errors / (total_extracted + errors)) * 100
        
        return metrics
    
    def _get_health_indicators(self) -> Dict[str, str]:
        """Get health indicators"""
        indicators = {}
        
        # Database connectivity
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT 1")
                indicators['database_connectivity'] = 'online'
        except Exception:
            indicators['database_connectivity'] = 'offline'
        
        # Data freshness
        latest_restaurant = self.safe_execute_query(
            "SELECT MAX(created_at) as latest FROM restaurants",
            fetch_one=True
        )
        
        if latest_restaurant and latest_restaurant['latest']:
            latest_time = latest_restaurant['latest']
            if isinstance(latest_time, str):
                latest_time = datetime.fromisoformat(latest_time)
            
            time_diff = datetime.now() - latest_time
            indicators['data_freshness'] = f'{time_diff.days}_days_old'
        
        return indicators
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance report statistics"""
        stats = self.get_base_statistics()
        
        stats['performance_report'] = {
            'session_stats': self.session_stats,
            'database_stats': self._get_database_stats(),
            'growth_stats': self._get_growth_stats(),
            'efficiency_metrics': self._get_efficiency_metrics(),
            'health_indicators': self._get_health_indicators()
        }
        
        return stats