#!/usr/bin/env python3
"""
Database Status - Database-specific monitoring and statistics
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from .status_base import StatusBase


class DatabaseStatus(StatusBase):
    """Database-specific monitoring and statistics"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Status do Banco de Dados", session_stats, data_dir)
    
    def show_database_status(self):
        """Show comprehensive database status"""
        print("\n🗄️ STATUS DO BANCO DE DADOS")
        print("═" * 50)
        
        # Connection status
        self._show_connection_status()
        
        # Database overview
        self._show_database_overview()
        
        # Table statistics
        self._show_table_statistics()
        
        # Performance metrics
        self._show_performance_metrics()
        
        # Recent activity
        self._show_recent_activity()
    
    def _show_connection_status(self):
        """Display database connection status"""
        print("\n🔌 Status da Conexão:")
        
        db_info = self.get_database_info()
        
        if db_info.get('connected', False):
            print(f"  {self.indicators['success']} Conectado")
            print(f"  Versão: {db_info.get('version', 'Unknown')}")
            
            # Connection pool status
            pool_info = self._get_connection_pool_info()
            if pool_info:
                print(f"  Pool de conexões: {pool_info.get('active', 0)}/{pool_info.get('size', 0)}")
        else:
            print(f"  {self.indicators['error']} Desconectado")
            if 'error' in db_info:
                print(f"  Erro: {db_info['error']}")
    
    def _show_database_overview(self):
        """Display database overview"""
        print("\n📊 Visão Geral:")
        
        try:
            # Database size and tables
            db_info = self.get_database_info()
            print(f"  Tamanho total: {self.format_bytes(db_info.get('size', 0))}")
            print(f"  Número de tabelas: {db_info.get('tables', 0)}")
            
            # Get detailed statistics
            stats = self._get_database_statistics()
            if stats:
                print(f"  Total de registros: {stats.get('total_records', 0):,}")
                print(f"  Índices: {stats.get('index_count', 0)}")
                print(f"  Tamanho dos índices: {self.format_bytes(stats.get('index_size', 0))}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter visão geral: {e}")
    
    def _show_table_statistics(self):
        """Display table statistics"""
        print("\n📋 Estatísticas das Tabelas:")
        
        try:
            tables = self._get_table_statistics()
            
            if tables:
                headers = ["Tabela", "Registros", "Tamanho", "Índices", "Última Atualização"]
                data = []
                
                for table in tables[:10]:  # Show top 10 tables
                    data.append([
                        table['name'],
                        f"{table['rows']:,}",
                        self.format_bytes(table['data_size']),
                        table['index_count'],
                        table['update_time'].strftime('%Y-%m-%d %H:%M') if table['update_time'] else 'N/A'
                    ])
                
                self.show_table(headers, data)
                
                if len(tables) > 10:
                    print(f"\n  ... e mais {len(tables) - 10} tabelas")
            else:
                print("  Nenhuma tabela encontrada")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas das tabelas: {e}")
    
    def _show_performance_metrics(self):
        """Display database performance metrics"""
        print("\n⚡ Métricas de Performance:")
        
        try:
            metrics = self._get_performance_metrics()
            
            if metrics:
                # Query statistics
                print(f"  Queries executadas: {metrics.get('queries', 0):,}")
                print(f"  Queries lentas: {metrics.get('slow_queries', 0):,}")
                print(f"  Tempo médio de query: {metrics.get('avg_query_time', 0):.2f}ms")
                
                # Connection statistics
                print(f"\n  Conexões totais: {metrics.get('total_connections', 0):,}")
                print(f"  Conexões ativas: {metrics.get('active_connections', 0)}")
                print(f"  Conexões abortadas: {metrics.get('aborted_connections', 0)}")
                
                # Cache statistics
                cache_ratio = metrics.get('cache_hit_ratio', 0)
                cache_status = self.format_status_indicator(cache_ratio, {'critical': 50, 'warning': 70})
                print(f"\n  Taxa de acerto do cache: {cache_status}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter métricas de performance: {e}")
    
    def _show_recent_activity(self):
        """Display recent database activity"""
        print("\n📈 Atividade Recente:")
        
        try:
            # Recent inserts
            recent_inserts = self._get_recent_inserts(limit=5)
            if recent_inserts:
                print("\n  Últimas inserções:")
                for record in recent_inserts:
                    print(f"    • {record['table']}: {record['count']} registros em {record['time']}")
            
            # Active queries
            active_queries = self._get_active_queries()
            if active_queries:
                print(f"\n  Queries ativas: {len(active_queries)}")
                for query in active_queries[:3]:
                    print(f"    • {query['query'][:50]}... ({query['time']}s)")
                    
        except Exception as e:
            self.show_error(f"Erro ao obter atividade recente: {e}")
    
    def show_table_details(self, table_name: str = None):
        """Show detailed information about a specific table"""
        if not table_name:
            # List available tables
            tables = self._get_table_list()
            if tables:
                print("\n📋 Tabelas disponíveis:")
                for i, table in enumerate(tables, 1):
                    print(f"  {i}. {table}")
                
                try:
                    choice = int(input("\nEscolha uma tabela (número): "))
                    if 1 <= choice <= len(tables):
                        table_name = tables[choice - 1]
                    else:
                        self.show_error("Opção inválida")
                        return
                except ValueError:
                    self.show_error("Entrada inválida")
                    return
            else:
                self.show_error("Nenhuma tabela encontrada")
                return
        
        print(f"\n🔍 DETALHES DA TABELA: {table_name}")
        print("═" * 50)
        
        try:
            # Table structure
            self._show_table_structure(table_name)
            
            # Table statistics
            self._show_table_stats(table_name)
            
            # Table indexes
            self._show_table_indexes(table_name)
            
            # Sample data
            self._show_sample_data(table_name)
            
        except Exception as e:
            self.show_error(f"Erro ao obter detalhes da tabela: {e}")
    
    def _get_connection_pool_info(self) -> Dict[str, Any]:
        """Get connection pool information"""
        try:
            # This is database-specific, example for MySQL
            result = self.safe_execute_query("""
                SELECT COUNT(*) as active 
                FROM information_schema.PROCESSLIST 
                WHERE USER = CURRENT_USER()
            """, fetch_one=True)
            
            if result:
                return {
                    'active': result[0],
                    'size': 5  # Default pool size, should be from config
                }
            
        except:
            pass
        
        return {}
    
    def _get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {}
        
        try:
            # Total records across all tables
            result = self.safe_execute_query("""
                SELECT SUM(TABLE_ROWS) as total_rows,
                       COUNT(DISTINCT INDEX_NAME) as index_count,
                       SUM(INDEX_LENGTH) as index_size
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_TYPE = 'BASE TABLE'
            """, fetch_one=True)
            
            if result:
                stats['total_records'] = result[0] or 0
                stats['index_count'] = result[1] or 0
                stats['index_size'] = result[2] or 0
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas: {e}")
        
        return stats
    
    def _get_table_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all tables"""
        tables = []
        
        try:
            results = self.safe_execute_query("""
                SELECT 
                    TABLE_NAME,
                    TABLE_ROWS,
                    DATA_LENGTH,
                    INDEX_LENGTH,
                    UPDATE_TIME,
                    (SELECT COUNT(*) FROM information_schema.STATISTICS 
                     WHERE TABLE_SCHEMA = t.TABLE_SCHEMA 
                     AND TABLE_NAME = t.TABLE_NAME) as index_count
                FROM information_schema.TABLES t
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY DATA_LENGTH + INDEX_LENGTH DESC
            """)
            
            if results:
                for row in results:
                    tables.append({
                        'name': row[0],
                        'rows': row[1] or 0,
                        'data_size': row[2] or 0,
                        'index_size': row[3] or 0,
                        'update_time': row[4],
                        'index_count': row[5] or 0
                    })
                    
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas das tabelas: {e}")
        
        return tables
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        metrics = {}
        
        try:
            # Query statistics
            result = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Questions'", fetch_one=True)
            if result:
                metrics['queries'] = int(result[1])
            
            result = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Slow_queries'", fetch_one=True)
            if result:
                metrics['slow_queries'] = int(result[1])
            
            # Connection statistics
            result = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Connections'", fetch_one=True)
            if result:
                metrics['total_connections'] = int(result[1])
            
            result = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Threads_connected'", fetch_one=True)
            if result:
                metrics['active_connections'] = int(result[1])
            
            result = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Aborted_connects'", fetch_one=True)
            if result:
                metrics['aborted_connections'] = int(result[1])
            
            # Cache statistics
            key_reads = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Key_reads'", fetch_one=True)
            key_read_requests = self.safe_execute_query("SHOW GLOBAL STATUS LIKE 'Key_read_requests'", fetch_one=True)
            
            if key_reads and key_read_requests:
                reads = int(key_reads[1])
                requests = int(key_read_requests[1])
                if requests > 0:
                    metrics['cache_hit_ratio'] = ((requests - reads) / requests) * 100
                    
        except Exception as e:
            self.show_error(f"Erro ao obter métricas: {e}")
        
        return metrics
    
    def _get_recent_inserts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent insert activity"""
        recent = []
        
        try:
            # Get tables ordered by update time
            results = self.safe_execute_query(f"""
                SELECT TABLE_NAME, TABLE_ROWS, UPDATE_TIME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND UPDATE_TIME IS NOT NULL
                ORDER BY UPDATE_TIME DESC
                LIMIT {limit}
            """)
            
            if results:
                for row in results:
                    if row[2]:  # If update_time exists
                        time_diff = datetime.now() - row[2]
                        recent.append({
                            'table': row[0],
                            'count': row[1] or 0,
                            'time': self.format_duration(time_diff.total_seconds())
                        })
                        
        except Exception as e:
            self.show_error(f"Erro ao obter inserções recentes: {e}")
        
        return recent
    
    def _get_active_queries(self) -> List[Dict[str, Any]]:
        """Get currently active queries"""
        queries = []
        
        try:
            results = self.safe_execute_query("""
                SELECT ID, USER, TIME, STATE, INFO
                FROM information_schema.PROCESSLIST
                WHERE COMMAND != 'Sleep' 
                  AND TIME > 0
                ORDER BY TIME DESC
                LIMIT 10
            """)
            
            if results:
                for row in results:
                    if row[4]:  # If query info exists
                        queries.append({
                            'id': row[0],
                            'user': row[1],
                            'time': row[2],
                            'state': row[3],
                            'query': row[4]
                        })
                        
        except Exception as e:
            self.show_error(f"Erro ao obter queries ativas: {e}")
        
        return queries
    
    def _get_table_list(self) -> List[str]:
        """Get list of all tables"""
        tables = []
        
        try:
            results = self.safe_execute_query("""
                SELECT TABLE_NAME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            if results:
                tables = [row[0] for row in results]
                
        except Exception as e:
            self.show_error(f"Erro ao listar tabelas: {e}")
        
        return tables
    
    def _show_table_structure(self, table_name: str):
        """Show table structure"""
        print("\n📐 Estrutura da Tabela:")
        
        try:
            results = self.safe_execute_query(f"DESCRIBE {table_name}")
            
            if results:
                headers = ["Campo", "Tipo", "Null", "Key", "Default", "Extra"]
                data = []
                
                for row in results:
                    data.append(list(row))
                
                self.show_table(headers, data)
                
        except Exception as e:
            self.show_error(f"Erro ao obter estrutura: {e}")
    
    def _show_table_stats(self, table_name: str):
        """Show table statistics"""
        print("\n📊 Estatísticas da Tabela:")
        
        try:
            result = self.safe_execute_query(f"""
                SELECT 
                    TABLE_ROWS,
                    DATA_LENGTH,
                    INDEX_LENGTH,
                    CREATE_TIME,
                    UPDATE_TIME,
                    TABLE_COLLATION
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = '{table_name}'
            """, fetch_one=True)
            
            if result:
                print(f"  Registros: {result[0]:,}")
                print(f"  Tamanho dos dados: {self.format_bytes(result[1])}")
                print(f"  Tamanho dos índices: {self.format_bytes(result[2])}")
                print(f"  Tamanho total: {self.format_bytes(result[1] + result[2])}")
                print(f"  Criada em: {result[3]}")
                print(f"  Última atualização: {result[4]}")
                print(f"  Collation: {result[5]}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas: {e}")
    
    def _show_table_indexes(self, table_name: str):
        """Show table indexes"""
        print("\n🔍 Índices da Tabela:")
        
        try:
            results = self.safe_execute_query(f"""
                SELECT 
                    INDEX_NAME,
                    NON_UNIQUE,
                    SEQ_IN_INDEX,
                    COLUMN_NAME,
                    INDEX_TYPE
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = '{table_name}'
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """)
            
            if results:
                current_index = None
                for row in results:
                    if row[0] != current_index:
                        current_index = row[0]
                        unique = "UNIQUE" if row[1] == 0 else "NON-UNIQUE"
                        print(f"\n  {row[0]} ({unique}, {row[4]}):")
                    print(f"    - {row[3]}")
            else:
                print("  Nenhum índice encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao obter índices: {e}")
    
    def _show_sample_data(self, table_name: str):
        """Show sample data from table"""
        print("\n📄 Amostra de Dados:")
        
        try:
            # Get column names
            columns_result = self.safe_execute_query(f"""
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
                LIMIT 5
            """)
            
            if columns_result:
                columns = [row[0] for row in columns_result]
                columns_str = ", ".join(columns)
                
                # Get sample data
                results = self.safe_execute_query(f"""
                    SELECT {columns_str}
                    FROM {table_name}
                    ORDER BY 1 DESC
                    LIMIT 5
                """)
                
                if results:
                    data = []
                    for row in results:
                        data.append([str(val)[:30] + '...' if str(val) and len(str(val)) > 30 else val for val in row])
                    
                    self.show_table(columns, data)
                else:
                    print("  Tabela vazia")
                    
        except Exception as e:
            self.show_error(f"Erro ao obter amostra: {e}")
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get database status statistics"""
        stats = self.get_base_statistics()
        
        # Add database-specific statistics
        stats['database_stats'] = self._get_database_statistics()
        stats['performance_metrics'] = self._get_performance_metrics()
        stats['table_count'] = len(self._get_table_list())
        
        # Connection health
        db_info = self.get_database_info()
        stats['connection_healthy'] = db_info.get('connected', False)
        
        return stats