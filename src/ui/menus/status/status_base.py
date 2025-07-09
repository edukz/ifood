#!/usr/bin/env python3
"""
Status Base - Base class for all status monitoring modules
"""

import os
import psutil
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
# Optional imports - sistema funciona sem eles
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    def tabulate(data, headers=None, **kwargs):
        """Fallback function for when tabulate is not available"""
        if not data:
            return "Nenhum dado disponível"
        
        result = []
        if headers:
            result.append("\t".join(str(h) for h in headers))
            result.append("-" * 50)
        
        for row in data:
            if isinstance(row, dict):
                result.append("\t".join(str(row.get(h, '')) for h in (headers or row.keys())))
            else:
                result.append("\t".join(str(cell) for cell in row))
        
        return "\n".join(result)

from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu


class StatusBase(BaseMenu):
    """Base class for status monitoring modules with common functionality"""
    
    def __init__(self, title: str, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__(title, session_stats, data_dir)
        self.db = get_database_manager()
        
        # Status indicators
        self.indicators = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'running': '🔄',
            'stopped': '⏹️',
            'critical': '🔴',
            'warning_level': '🟡',
            'healthy': '🟢'
        }
    
    def format_status_indicator(self, value: float, thresholds: Dict[str, float]) -> str:
        """
        Format status indicator based on value and thresholds
        
        Args:
            value: Current value to evaluate
            thresholds: Dictionary with 'critical' and 'warning' thresholds
            
        Returns:
            Formatted string with appropriate indicator
        """
        critical = thresholds.get('critical', 90)
        warning = thresholds.get('warning', 70)
        
        if value >= critical:
            return f"{self.indicators['critical']} {value:.1f}%"
        elif value >= warning:
            return f"{self.indicators['warning_level']} {value:.1f}%"
        else:
            return f"{self.indicators['healthy']} {value:.1f}%"
    
    def safe_execute_query(self, query: str, params: Tuple = None, fetch_one: bool = False) -> Optional[Any]:
        """
        Safely execute database query with error handling
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch one or all results
            
        Returns:
            Query result or None if error
        """
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
                    
        except Exception as e:
            self.show_error(f"Erro na consulta SQL: {e}")
            return None
    
    def get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage
        
        Returns:
            Dictionary with resource usage information
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            net_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'per_cpu': psutil.cpu_percent(interval=0.1, percpu=True)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
            
        except Exception as e:
            self.show_error(f"Erro ao obter recursos do sistema: {e}")
            return {}
    
    def format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human-readable format
        
        Args:
            bytes_value: Number of bytes
            
        Returns:
            Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    def show_table(self, headers: List[str], data: List[List[Any]], title: str = None):
        """
        Display data in a formatted table
        
        Args:
            headers: Table headers
            data: Table data
            title: Optional table title
        """
        if title:
            print(f"\n{title}")
            print("═" * len(title))
        
        if data:
            print(tabulate(data, headers=headers, tablefmt="simple"))
        else:
            print("Nenhum dado disponível")
    
    def calculate_health_score(self, checks: Dict[str, bool]) -> Tuple[float, str]:
        """
        Calculate overall health score based on checks
        
        Args:
            checks: Dictionary of check_name: passed (bool)
            
        Returns:
            Tuple of (score, status_text)
        """
        if not checks:
            return 0.0, "Sem dados"
        
        passed = sum(1 for check in checks.values() if check)
        total = len(checks)
        score = (passed / total) * 100
        
        if score >= 90:
            status = "Excelente"
        elif score >= 75:
            status = "Bom"
        elif score >= 60:
            status = "Regular"
        elif score >= 40:
            status = "Ruim"
        else:
            status = "Crítico"
        
        return score, status
    
    def check_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Check if a service/process is running
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Dictionary with service status information
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                if service_name.lower() in proc.info['name'].lower():
                    return {
                        'running': True,
                        'pid': proc.info['pid'],
                        'status': proc.info['status'],
                        'memory': proc.memory_info().rss if proc.is_running() else 0
                    }
            
            return {'running': False}
            
        except Exception as e:
            return {'running': False, 'error': str(e)}
    
    def parse_log_file(self, log_path: Path, lines: int = 100) -> List[Dict[str, Any]]:
        """
        Parse log file and extract relevant information
        
        Args:
            log_path: Path to log file
            lines: Number of lines to read from end
            
        Returns:
            List of parsed log entries
        """
        entries = []
        
        try:
            if not log_path.exists():
                return entries
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last N lines efficiently
                log_lines = f.readlines()[-lines:]
            
            for line in log_lines:
                # Basic log parsing - can be enhanced based on log format
                entry = {
                    'raw': line.strip(),
                    'timestamp': None,
                    'level': 'INFO',
                    'message': line.strip()
                }
                
                # Try to extract timestamp
                if line.startswith('[') and ']' in line:
                    timestamp_end = line.index(']')
                    timestamp_str = line[1:timestamp_end]
                    try:
                        entry['timestamp'] = datetime.fromisoformat(timestamp_str)
                    except:
                        pass
                
                # Try to extract log level
                for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'CRITICAL']:
                    if level in line.upper():
                        entry['level'] = level
                        break
                
                entries.append(entry)
            
        except Exception as e:
            self.show_error(f"Erro ao ler log {log_path}: {e}")
        
        return entries
    
    def test_connectivity(self, host: str = "www.google.com", port: int = 80, timeout: int = 5) -> bool:
        """
        Test network connectivity
        
        Args:
            host: Host to test
            port: Port to test
            timeout: Timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        import socket
        
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get basic database information
        
        Returns:
            Dictionary with database statistics
        """
        info = {
            'connected': False,
            'tables': 0,
            'size': 0,
            'version': 'Unknown'
        }
        
        try:
            # Test connection
            with self.db.get_cursor() as (cursor, _):
                # Get version
                cursor.execute("SELECT VERSION()")
                result = cursor.fetchone()
                if result:
                    info['version'] = result[0]
                
                # Get table count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """)
                result = cursor.fetchone()
                if result:
                    info['tables'] = result[0]
                
                # Get database size
                cursor.execute("""
                    SELECT SUM(data_length + index_length)
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    info['size'] = result[0]
                
                info['connected'] = True
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def get_process_info(self) -> Dict[str, Any]:
        """
        Get current process information
        
        Returns:
            Dictionary with process statistics
        """
        try:
            process = psutil.Process(os.getpid())
            
            return {
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_rss': process.memory_info().rss,
                'memory_vms': process.memory_info().vms,
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections()),
                'create_time': datetime.fromtimestamp(process.create_time()),
                'uptime': datetime.now() - datetime.fromtimestamp(process.create_time())
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_base_statistics(self) -> Dict[str, Any]:
        """Get base status statistics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_resources': self.get_system_resources(),
            'database_info': self.get_database_info(),
            'process_info': self.get_process_info(),
            'connectivity': self.test_connectivity()
        }