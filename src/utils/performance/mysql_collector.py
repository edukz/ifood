#!/usr/bin/env python3
"""
MySQL Collector - MySQL database metrics collection
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import PerformanceMetric
from src.config.database import execute_query
from src.utils.logger import setup_logger

logger = setup_logger("MySQLCollector")


class MySQLCollector:
    """Coletor de métricas específicas do MySQL"""
    
    def __init__(self):
        self.logger = logger
        self._last_queries: Optional[float] = None
        self._last_query_time: Optional[datetime] = None
        
        # Tables to monitor
        self.monitored_tables = ['categories', 'restaurants', 'products']
    
    def collect_mysql_metrics(self) -> List[PerformanceMetric]:
        """Coleta métricas específicas do MySQL"""
        now = datetime.now()
        metrics = []
        
        try:
            # Connection metrics
            metrics.extend(self._collect_connection_metrics(now))
            
            # Query performance metrics
            metrics.extend(self._collect_query_metrics(now))
            
            # Table size metrics
            metrics.extend(self._collect_table_metrics(now))
            
            # Database status metrics
            metrics.extend(self._collect_status_metrics(now))
            
        except Exception as e:
            self.logger.error(f"Erro geral ao coletar métricas MySQL: {e}")
        
        return metrics
    
    def _collect_connection_metrics(self, now: datetime) -> List[PerformanceMetric]:
        """Coleta métricas de conexão"""
        metrics = []
        
        try:
            # Conexões ativas
            connections = execute_query("SHOW STATUS LIKE 'Threads_connected'", fetch_all=True)
            if connections:
                metrics.append(PerformanceMetric(
                    name="mysql_connections",
                    value=float(connections[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
            
            # Conexões máximas
            max_connections = execute_query("SHOW VARIABLES LIKE 'max_connections'", fetch_all=True)
            if max_connections:
                metrics.append(PerformanceMetric(
                    name="mysql_max_connections",
                    value=float(max_connections[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
            
            # Threads running
            threads_running = execute_query("SHOW STATUS LIKE 'Threads_running'", fetch_all=True)
            if threads_running:
                metrics.append(PerformanceMetric(
                    name="mysql_threads_running",
                    value=float(threads_running[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de conexão: {e}")
        
        return metrics
    
    def _collect_query_metrics(self, now: datetime) -> List[PerformanceMetric]:
        """Coleta métricas de performance de queries"""
        metrics = []
        
        try:
            # Total queries
            queries = execute_query("SHOW STATUS LIKE 'Queries'", fetch_all=True)
            if queries:
                current_queries = float(queries[0]['Value'])
                
                # Calculate QPS (queries per second)
                if self._last_queries is not None and self._last_query_time is not None:
                    time_diff = (now - self._last_query_time).total_seconds()
                    if time_diff > 0:
                        qps = (current_queries - self._last_queries) / time_diff
                        metrics.append(PerformanceMetric(
                            name="mysql_qps",
                            value=qps,
                            unit="queries/second",
                            timestamp=now,
                            category="mysql"
                        ))
                
                # Update last values
                self._last_queries = current_queries
                self._last_query_time = now
                
                # Total queries metric
                metrics.append(PerformanceMetric(
                    name="mysql_total_queries",
                    value=current_queries,
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
            
            # Slow queries
            slow_queries = execute_query("SHOW STATUS LIKE 'Slow_queries'", fetch_all=True)
            if slow_queries:
                metrics.append(PerformanceMetric(
                    name="mysql_slow_queries",
                    value=float(slow_queries[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
            
            # Questions
            questions = execute_query("SHOW STATUS LIKE 'Questions'", fetch_all=True)
            if questions:
                metrics.append(PerformanceMetric(
                    name="mysql_questions",
                    value=float(questions[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de query: {e}")
        
        return metrics
    
    def _collect_table_metrics(self, now: datetime) -> List[PerformanceMetric]:
        """Coleta métricas de tabelas"""
        metrics = []
        
        try:
            # Tamanho das tabelas principais
            tables_size = execute_query("""
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                    table_rows
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name IN ('products', 'restaurants', 'categories')
            """, fetch_all=True)
            
            for table in tables_size or []:
                table_name = table.get('table_name') or table.get('TABLE_NAME', 'unknown')
                size_mb = table.get('size_mb') or table.get('SIZE_MB', 0)
                table_rows = table.get('table_rows') or table.get('TABLE_ROWS', 0)
                
                # Table size metric
                metrics.append(PerformanceMetric(
                    name=f"table_size_{table_name}",
                    value=float(size_mb),
                    unit="MB",
                    timestamp=now,
                    category="mysql",
                    metadata={'table': table_name}
                ))
                
                # Table rows metric
                metrics.append(PerformanceMetric(
                    name=f"table_rows_{table_name}",
                    value=float(table_rows),
                    unit="rows",
                    timestamp=now,
                    category="mysql",
                    metadata={'table': table_name}
                ))
            
            # Contagem precisa de registros
            for table in self.monitored_tables:
                try:
                    count_result = execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch_one=True)
                    if count_result:
                        # Safely extract count value
                        if isinstance(count_result, dict):
                            count_value = count_result.get('count', 0)
                        elif isinstance(count_result, (list, tuple)) and len(count_result) > 0:
                            count_value = count_result[0]
                        else:
                            count_value = count_result
                        
                        metrics.append(PerformanceMetric(
                            name=f"table_count_{table}",
                            value=float(count_value if count_value is not None else 0),
                            unit="rows",
                            timestamp=now,
                            category="mysql",
                            metadata={'table': table}
                        ))
                except Exception as e:
                    self.logger.error(f"Erro ao contar registros da tabela {table}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de tabelas: {e}")
        
        return metrics
    
    def _collect_status_metrics(self, now: datetime) -> List[PerformanceMetric]:
        """Coleta métricas de status do MySQL"""
        metrics = []
        
        try:
            # InnoDB buffer pool
            buffer_pool_size = execute_query("SHOW STATUS LIKE 'Innodb_buffer_pool_size'", fetch_all=True)
            if buffer_pool_size:
                metrics.append(PerformanceMetric(
                    name="mysql_buffer_pool_size",
                    value=float(buffer_pool_size[0]['Value']) / (1024**2),  # MB
                    unit="MB",
                    timestamp=now,
                    category="mysql"
                ))
            
            # InnoDB buffer pool usage
            buffer_pool_pages = execute_query("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_total'", fetch_all=True)
            buffer_pool_free = execute_query("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_free'", fetch_all=True)
            
            if buffer_pool_pages and buffer_pool_free:
                total_pages = float(buffer_pool_pages[0]['Value'])
                free_pages = float(buffer_pool_free[0]['Value'])
                if total_pages > 0:
                    usage_percent = ((total_pages - free_pages) / total_pages) * 100
                    metrics.append(PerformanceMetric(
                        name="mysql_buffer_pool_usage",
                        value=usage_percent,
                        unit="percent",
                        timestamp=now,
                        category="mysql"
                    ))
            
            # Uptime
            uptime = execute_query("SHOW STATUS LIKE 'Uptime'", fetch_all=True)
            if uptime:
                metrics.append(PerformanceMetric(
                    name="mysql_uptime",
                    value=float(uptime[0]['Value']),
                    unit="seconds",
                    timestamp=now,
                    category="mysql"
                ))
            
            # Aborted connections
            aborted_connects = execute_query("SHOW STATUS LIKE 'Aborted_connects'", fetch_all=True)
            if aborted_connects:
                metrics.append(PerformanceMetric(
                    name="mysql_aborted_connects",
                    value=float(aborted_connects[0]['Value']),
                    unit="count",
                    timestamp=now,
                    category="mysql"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de status: {e}")
        
        return metrics
    
    def test_connection(self) -> bool:
        """Testa conexão com MySQL"""
        try:
            result = execute_query("SELECT 1 as test", fetch_one=True)
            return result is not None
        except Exception as e:
            self.logger.error(f"Erro ao testar conexão MySQL: {e}")
            return False
    
    def get_mysql_version(self) -> str:
        """Retorna versão do MySQL"""
        try:
            version = execute_query("SELECT VERSION() as version", fetch_one=True)
            if version:
                if isinstance(version, dict):
                    return version.get('version', 'unknown')
                else:
                    return str(version)
            return 'unknown'
        except Exception as e:
            self.logger.error(f"Erro ao obter versão MySQL: {e}")
            return 'unknown'
    
    def get_database_info(self) -> Dict[str, Any]:
        """Retorna informações da base de dados"""
        try:
            info = {
                'mysql_version': self.get_mysql_version(),
                'connection_status': self.test_connection(),
                'monitored_tables': self.monitored_tables
            }
            
            # Database name
            db_name = execute_query("SELECT DATABASE() as db", fetch_one=True)
            if db_name:
                if isinstance(db_name, dict):
                    info['database_name'] = db_name.get('db', 'unknown')
                else:
                    info['database_name'] = str(db_name)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da base de dados: {e}")
            return {'error': str(e)}


# Export the collector
__all__ = ['MySQLCollector']