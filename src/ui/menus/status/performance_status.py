#!/usr/bin/env python3
"""
Performance Status - Performance metrics and benchmarks
"""

import time
from typing import Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from .status_base import StatusBase


class PerformanceStatus(StatusBase):
    """Performance metrics and benchmarks"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Métricas de Performance", session_stats, data_dir)
    
    def show_performance_metrics(self):
        """Show comprehensive performance metrics"""
        print("\n🎯 MÉTRICAS DE PERFORMANCE")
        print("═" * 50)
        
        # System metrics
        self._show_system_metrics()
        
        # Scraping metrics
        self._show_scraping_metrics()
        
        # Database metrics
        self._show_database_metrics()
        
        # Error metrics
        self._show_error_metrics()
        
        # Performance trends
        self._show_performance_trends()
        
        # Benchmark comparison
        self._show_benchmark_comparison()
        
        # Performance recommendations
        self._show_performance_recommendations()
    
    def _show_system_metrics(self):
        """Display system performance metrics"""
        print("⚡ MÉTRICAS DE SISTEMA:")
        
        try:
            # Database response time
            start_time = time.time()
            try:
                with self.db.get_cursor() as (cursor, _):
                    cursor.execute("SELECT 1")
                    db_response_time = (time.time() - start_time) * 1000
                    print(f"  🕐 Tempo de resposta do banco: {db_response_time:.2f}ms")
            except Exception as e:
                print(f"  ❌ Erro no banco: {e}")
            
            # System resources
            resources = self.get_system_resources()
            if resources:
                print(f"  🖥️ CPU: {resources['cpu']['percent']:.1f}%")
                print(f"  💾 Memória: {resources['memory']['percent']:.1f}%")
                print(f"  💿 Disco: {resources['disk']['percent']:.1f}%")
            
            # I/O metrics
            self._show_io_metrics()
            
        except Exception as e:
            self.show_error(f"Erro ao obter métricas do sistema: {e}")
    
    def _show_io_metrics(self):
        """Show I/O performance metrics"""
        try:
            import psutil
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                print(f"  📥 Operações de leitura: {disk_io.read_count:,}")
                print(f"  📤 Operações de escrita: {disk_io.write_count:,}")
                print(f"  📊 Throughput de leitura: {disk_io.read_bytes / (1024**2):.1f} MB")
                print(f"  📊 Throughput de escrita: {disk_io.write_bytes / (1024**2):.1f} MB")
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                print(f"  🌐 Dados enviados: {net_io.bytes_sent / (1024**2):.1f} MB")
                print(f"  🌐 Dados recebidos: {net_io.bytes_recv / (1024**2):.1f} MB")
                print(f"  📦 Pacotes enviados: {net_io.packets_sent:,}")
                print(f"  📦 Pacotes recebidos: {net_io.packets_recv:,}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter métricas de I/O: {e}")
    
    def _show_scraping_metrics(self):
        """Show scraping performance metrics"""
        print(f"\n🔍 MÉTRICAS DE SCRAPING:")
        
        try:
            # Calculate metrics based on current session
            total_extracted = (
                self.session_stats.get('categories_extracted', 0) +
                self.session_stats.get('restaurants_extracted', 0) +
                self.session_stats.get('products_extracted', 0)
            )
            
            execution_time = self.session_stats.get('execution_time', 0)
            
            print(f"  📊 Total extraído: {total_extracted:,} itens")
            print(f"  ⏱️ Tempo de execução: {execution_time:.2f} segundos")
            
            if execution_time > 0:
                throughput = total_extracted / execution_time
                print(f"  ⚡ Throughput: {throughput:.2f} itens/segundo")
            
            # Detailed metrics by type
            self._show_detailed_scraping_metrics()
            
        except Exception as e:
            self.show_error(f"Erro ao obter métricas de scraping: {e}")
    
    def _show_detailed_scraping_metrics(self):
        """Show detailed scraping metrics by type"""
        print(f"\n📈 MÉTRICAS DETALHADAS:")
        
        # Performance data for different types
        types_metrics = [
            ("Categorias", self.session_stats.get('categories_extracted', 0), 2.5),
            ("Restaurantes", self.session_stats.get('restaurants_extracted', 0), 15),
            ("Produtos", self.session_stats.get('products_extracted', 0), 3)
        ]
        
        headers = ['Tipo', 'Extraídos', 'Tempo/Item', 'Tempo Total', 'Eficiência']
        data = []
        
        for item_type, count, avg_time in types_metrics:
            estimated_time = count * avg_time
            efficiency = (count / estimated_time * 100) if estimated_time > 0 else 0
            
            data.append([
                item_type,
                f"{count:,}",
                f"{avg_time:.1f}s",
                f"{estimated_time:.1f}s",
                f"{efficiency:.1f}%"
            ])
        
        self.show_table(headers, data)
    
    def _show_database_metrics(self):
        """Show database performance metrics"""
        print(f"\n💾 MÉTRICAS DO BANCO DE DADOS:")
        
        try:
            # Test multiple queries to get average response time
            query_times = []
            test_queries = [
                "SELECT COUNT(*) FROM restaurants",
                "SELECT COUNT(*) FROM products",
                "SELECT COUNT(*) FROM categories",
                "SELECT VERSION()",
                "SHOW STATUS LIKE 'Threads_connected'"
            ]
            
            for query in test_queries:
                start_time = time.time()
                try:
                    result = self.safe_execute_query(query, fetch_one=True)
                    query_time = (time.time() - start_time) * 1000
                    query_times.append(query_time)
                except Exception:
                    continue
            
            if query_times:
                avg_query_time = sum(query_times) / len(query_times)
                min_query_time = min(query_times)
                max_query_time = max(query_times)
                
                print(f"  ⏱️ Tempo médio de query: {avg_query_time:.2f}ms")
                print(f"  🚀 Query mais rápida: {min_query_time:.2f}ms")
                print(f"  🐌 Query mais lenta: {max_query_time:.2f}ms")
            
            # Database-specific metrics
            self._show_database_specific_metrics()
            
        except Exception as e:
            self.show_error(f"Erro ao obter métricas do banco: {e}")
    
    def _show_database_specific_metrics(self):
        """Show database-specific performance metrics"""
        try:
            # Connection count
            result = self.safe_execute_query("SHOW STATUS LIKE 'Threads_connected'", fetch_one=True)
            if result:
                print(f"  🔗 Conexões ativas: {result[1]}")
            
            # Query cache statistics
            result = self.safe_execute_query("SHOW STATUS LIKE 'Qcache_hits'", fetch_one=True)
            if result:
                cache_hits = int(result[1])
                
                result = self.safe_execute_query("SHOW STATUS LIKE 'Qcache_inserts'", fetch_one=True)
                if result:
                    cache_inserts = int(result[1])
                    
                    if cache_hits + cache_inserts > 0:
                        cache_hit_ratio = (cache_hits / (cache_hits + cache_inserts)) * 100
                        print(f"  🎯 Taxa de acerto do cache: {cache_hit_ratio:.1f}%")
            
            # Table sizes
            result = self.safe_execute_query("""
                SELECT table_name, table_rows, data_length, index_length
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                ORDER BY data_length + index_length DESC
                LIMIT 5
            """)
            
            if result:
                print(f"  📊 Top 5 tabelas maiores:")
                for row in result:
                    table_name, rows, data_size, index_size = row
                    total_size = (data_size or 0) + (index_size or 0)
                    print(f"    {table_name}: {rows or 0:,} rows, {self.format_bytes(total_size)}")
                    
        except Exception as e:
            self.show_error(f"Erro ao obter métricas específicas do banco: {e}")
    
    def _show_error_metrics(self):
        """Show error performance metrics"""
        print(f"\n🚨 MÉTRICAS DE ERRO:")
        
        try:
            # Analyze logs for errors
            log_file = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
            
            if not log_file.exists():
                print("  📝 Nenhum log encontrado para hoje")
                return
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            error_count = content.count(' - ERROR - ')
            warning_count = content.count(' - WARNING - ')
            info_count = content.count(' - INFO - ')
            
            total_logs = error_count + warning_count + info_count
            
            if total_logs > 0:
                error_rate = (error_count / total_logs) * 100
                warning_rate = (warning_count / total_logs) * 100
                
                print(f"  📝 Total de logs: {total_logs:,}")
                print(f"  ❌ Erros: {error_count:,} ({error_rate:.1f}%)")
                print(f"  ⚠️ Avisos: {warning_count:,} ({warning_rate:.1f}%)")
                print(f"  ℹ️ Info: {info_count:,}")
                
                # Success rate
                success_rate = 100 - error_rate
                print(f"  ✅ Taxa de sucesso: {success_rate:.1f}%")
                
                # Error temporal analysis
                self._analyze_error_temporal_patterns(content)
            else:
                print("  ✅ Nenhum log encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao analisar métricas de erro: {e}")
    
    def _analyze_error_temporal_patterns(self, content: str):
        """Analyze temporal patterns in errors"""
        lines = content.split('\n')
        error_times = []
        
        for line in lines:
            if ' - ERROR - ' in line:
                timestamp_str = line.split(' - ')[0]
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    error_times.append(timestamp)
                except ValueError:
                    continue
        
        if len(error_times) > 1:
            # Calculate intervals between errors
            intervals = []
            for i in range(1, len(error_times)):
                interval = (error_times[i] - error_times[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                print(f"  ⏱️ Intervalo médio entre erros: {self.format_duration(avg_interval)}")
                
                # Error frequency in last hour
                now = datetime.now()
                recent_errors = [t for t in error_times if t > now - timedelta(hours=1)]
                if recent_errors:
                    print(f"  🔥 Erros na última hora: {len(recent_errors)}")
    
    def _show_performance_trends(self):
        """Show performance trends"""
        print(f"\n📊 TENDÊNCIAS DE PERFORMANCE:")
        
        try:
            # Current metrics
            current_time = datetime.now()
            resources = self.get_system_resources()
            
            if resources:
                cpu_percent = resources['cpu']['percent']
                memory_percent = resources['memory']['percent']
                
                print(f"  🕐 {current_time.strftime('%H:%M:%S')} - CPU: {cpu_percent:.1f}% | Mem: {memory_percent:.1f}%")
                
                # Simulate trend analysis (in a real implementation, you'd store historical data)
                self._simulate_trend_analysis(cpu_percent, memory_percent)
            
        except Exception as e:
            self.show_error(f"Erro ao analisar tendências: {e}")
    
    def _simulate_trend_analysis(self, cpu_percent: float, memory_percent: float):
        """Simulate trend analysis with current data"""
        # This would be replaced with actual historical data in a real implementation
        print(f"  📈 Análise de tendência (simulada):")
        
        if cpu_percent > 70:
            print(f"    🔴 CPU em tendência alta: {cpu_percent:.1f}%")
        elif cpu_percent < 30:
            print(f"    🟢 CPU em tendência baixa: {cpu_percent:.1f}%")
        else:
            print(f"    🟡 CPU estável: {cpu_percent:.1f}%")
        
        if memory_percent > 75:
            print(f"    🔴 Memória em tendência alta: {memory_percent:.1f}%")
        elif memory_percent < 40:
            print(f"    🟢 Memória em tendência baixa: {memory_percent:.1f}%")
        else:
            print(f"    🟡 Memória estável: {memory_percent:.1f}%")
    
    def _show_benchmark_comparison(self):
        """Show benchmark comparison"""
        print(f"\n🎯 COMPARAÇÃO COM BENCHMARKS:")
        
        try:
            # Define benchmarks
            benchmarks = {
                "Throughput médio": (1.5, "itens/segundo"),
                "Taxa de erro": (5, "%"),
                "Uso de CPU": (50, "%"),
                "Uso de memória": (60, "%"),
                "Tempo de resposta DB": (100, "ms")
            }
            
            # Calculate current metrics
            current_metrics = self._calculate_current_metrics()
            
            # Compare with benchmarks
            for metric, (benchmark, unit) in benchmarks.items():
                if metric in current_metrics:
                    current_value = current_metrics[metric]
                    
                    if metric in ["Taxa de erro", "Uso de CPU", "Uso de memória", "Tempo de resposta DB"]:
                        # Lower is better
                        if current_value < benchmark:
                            status = "🟢"
                        elif current_value < benchmark * 1.5:
                            status = "🟡"
                        else:
                            status = "🔴"
                    else:
                        # Higher is better
                        if current_value > benchmark:
                            status = "🟢"
                        elif current_value > benchmark * 0.7:
                            status = "🟡"
                        else:
                            status = "🔴"
                    
                    print(f"  {status} {metric}: {current_value:.1f}{unit} (benchmark: {benchmark}{unit})")
                else:
                    print(f"  ⚪ {metric}: Não disponível")
            
        except Exception as e:
            self.show_error(f"Erro na comparação com benchmarks: {e}")
    
    def _calculate_current_metrics(self) -> Dict[str, float]:
        """Calculate current performance metrics"""
        metrics = {}
        
        try:
            # Calculate throughput
            total_extracted = (
                self.session_stats.get('categories_extracted', 0) +
                self.session_stats.get('restaurants_extracted', 0) +
                self.session_stats.get('products_extracted', 0)
            )
            execution_time = self.session_stats.get('execution_time', 0)
            
            if execution_time > 0:
                metrics["Throughput médio"] = total_extracted / execution_time
            
            # Get system resources
            resources = self.get_system_resources()
            if resources:
                metrics["Uso de CPU"] = resources['cpu']['percent']
                metrics["Uso de memória"] = resources['memory']['percent']
            
            # Calculate database response time
            start_time = time.time()
            self.safe_execute_query("SELECT 1", fetch_one=True)
            metrics["Tempo de resposta DB"] = (time.time() - start_time) * 1000
            
            # Calculate error rate from logs
            error_rate = self._calculate_error_rate()
            if error_rate is not None:
                metrics["Taxa de erro"] = error_rate
            
        except Exception as e:
            self.show_error(f"Erro ao calcular métricas: {e}")
        
        return metrics
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from logs"""
        try:
            log_file = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
            
            if not log_file.exists():
                return None
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            error_count = content.count(' - ERROR - ')
            warning_count = content.count(' - WARNING - ')
            info_count = content.count(' - INFO - ')
            
            total_logs = error_count + warning_count + info_count
            
            if total_logs > 0:
                return (error_count / total_logs) * 100
            
        except Exception:
            pass
        
        return None
    
    def _show_performance_recommendations(self):
        """Show performance recommendations"""
        print(f"\n💡 RECOMENDAÇÕES DE PERFORMANCE:")
        
        try:
            recommendations = []
            
            # Get current metrics
            resources = self.get_system_resources()
            if resources:
                cpu_percent = resources['cpu']['percent']
                memory_percent = resources['memory']['percent']
                
                if cpu_percent > 80:
                    recommendations.append("🔧 Considere reduzir o número de workers paralelos")
                
                if memory_percent > 80:
                    recommendations.append("💾 Considere aumentar o intervalo de limpeza de cache")
                
                if resources['disk']['percent'] > 90:
                    recommendations.append("🗂️ Limpe arquivos temporários e logs antigos")
            
            # Check throughput
            total_extracted = (
                self.session_stats.get('categories_extracted', 0) +
                self.session_stats.get('restaurants_extracted', 0) +
                self.session_stats.get('products_extracted', 0)
            )
            execution_time = self.session_stats.get('execution_time', 0)
            
            if execution_time > 0:
                throughput = total_extracted / execution_time
                if throughput < 1:
                    recommendations.append("⚡ Considere otimizar as queries do banco de dados")
                    recommendations.append("🔄 Verifique a conectividade de rede")
            
            # Check error rate
            error_rate = self._calculate_error_rate()
            if error_rate and error_rate > 10:
                recommendations.append("🚨 Investigue os erros mais frequentes")
                recommendations.append("🔧 Considere implementar retry automático")
            
            # Database response time
            start_time = time.time()
            self.safe_execute_query("SELECT 1", fetch_one=True)
            db_response_time = (time.time() - start_time) * 1000
            
            if db_response_time > 500:
                recommendations.append("🗄️ Otimize índices do banco de dados")
                recommendations.append("🔧 Considere usar connection pooling")
            
            # Show recommendations
            if recommendations:
                for rec in recommendations:
                    print(f"  {rec}")
            else:
                print("  ✅ Sistema operando com performance adequada")
            
        except Exception as e:
            self.show_error(f"Erro ao gerar recomendações: {e}")
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance status statistics"""
        stats = self.get_base_statistics()
        
        # Add performance-specific statistics
        stats['performance_metrics'] = self._get_performance_metrics()
        stats['benchmark_comparison'] = self._get_benchmark_comparison()
        stats['recommendations'] = self._get_performance_recommendations()
        
        return stats
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            return self._calculate_current_metrics()
        except Exception as e:
            return {'error': str(e)}
    
    def _get_benchmark_comparison(self) -> Dict[str, Any]:
        """Get benchmark comparison"""
        try:
            benchmarks = {
                "Throughput médio": 1.5,
                "Taxa de erro": 5,
                "Uso de CPU": 50,
                "Uso de memória": 60,
                "Tempo de resposta DB": 100
            }
            
            current_metrics = self._calculate_current_metrics()
            
            comparison = {}
            for metric, benchmark in benchmarks.items():
                if metric in current_metrics:
                    current_value = current_metrics[metric]
                    comparison[metric] = {
                        'current': current_value,
                        'benchmark': benchmark,
                        'ratio': current_value / benchmark if benchmark > 0 else 0
                    }
            
            return comparison
        except Exception as e:
            return {'error': str(e)}
    
    def _get_performance_recommendations(self) -> List[str]:
        """Get performance recommendations"""
        try:
            recommendations = []
            
            resources = self.get_system_resources()
            if resources:
                if resources['cpu']['percent'] > 80:
                    recommendations.append("Reduce parallel workers")
                if resources['memory']['percent'] > 80:
                    recommendations.append("Increase cache cleanup interval")
                if resources['disk']['percent'] > 90:
                    recommendations.append("Clean temporary files")
            
            return recommendations
        except Exception as e:
            return [f"Error generating recommendations: {e}"]