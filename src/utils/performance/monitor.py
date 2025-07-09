#!/usr/bin/env python3
"""
Performance Monitor - Main performance monitoring orchestrator
"""

import time
import threading
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .metrics_collector import MetricsCollector
from .system_collector import SystemCollector
from .mysql_collector import MySQLCollector
from .alert_manager import AlertManager
from .models import PerformanceMetric
from src.config.database import get_retry_status
from src.utils.logger import setup_logger

logger = setup_logger("PerformanceMonitor")


class PerformanceMonitor:
    """Monitor principal de performance - orquestra todos os coletores"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        
        # Initialize all components
        self.metrics_collector = MetricsCollector()
        self.system_collector = SystemCollector()
        self.mysql_collector = MySQLCollector()
        self.alert_manager = AlertManager()
        
        # Threading control
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.collection_stats = {
            'total_collections': 0,
            'failed_collections': 0,
            'last_collection_time': None,
            'avg_collection_duration': 0.0
        }
        
        self.logger = logger
        self.logger.info("PerformanceMonitor inicializado")
    
    def start(self):
        """Inicia monitoramento em background"""
        if self.running:
            self.logger.warning("Monitor já está rodando")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"Performance Monitor iniciado (intervalo: {self.collection_interval}s)")
    
    def stop(self):
        """Para monitoramento"""
        if not self.running:
            return
            
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Performance Monitor parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        self.logger.info("Iniciando loop de monitoramento")
        
        while self.running:
            collection_start = time.time()
            
            try:
                # Coleta métricas de todos os coletores
                all_metrics = self._collect_all_metrics()
                
                # Registra métricas
                for metric in all_metrics:
                    self.metrics_collector.record_metric(metric)
                
                # Verifica alertas
                self.alert_manager.check_alerts(all_metrics)
                
                # Atualiza estatísticas de coleta
                collection_duration = time.time() - collection_start
                self._update_collection_stats(collection_duration, success=True)
                
                self.logger.debug(f"Coleta completada: {len(all_metrics)} métricas em {collection_duration:.2f}s")
                
            except Exception as e:
                collection_duration = time.time() - collection_start
                self._update_collection_stats(collection_duration, success=False)
                self.logger.error(f"Erro no loop de monitoramento: {e}")
            
            # Aguarda próxima coleta
            time.sleep(self.collection_interval)
        
        self.logger.info("Loop de monitoramento finalizado")
    
    def _collect_all_metrics(self) -> List[PerformanceMetric]:
        """Coleta métricas de todos os coletores"""
        all_metrics = []
        
        try:
            # System metrics
            system_metrics = self.system_collector.collect_system_metrics()
            all_metrics.extend(system_metrics)
            self.logger.debug(f"Coletadas {len(system_metrics)} métricas de sistema")
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de sistema: {e}")
        
        try:
            # MySQL metrics
            mysql_metrics = self.mysql_collector.collect_mysql_metrics()
            all_metrics.extend(mysql_metrics)
            self.logger.debug(f"Coletadas {len(mysql_metrics)} métricas de MySQL")
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de MySQL: {e}")
        
        return all_metrics
    
    def _update_collection_stats(self, duration: float, success: bool):
        """Atualiza estatísticas de coleta"""
        self.collection_stats['total_collections'] += 1
        self.collection_stats['last_collection_time'] = datetime.now()
        
        if not success:
            self.collection_stats['failed_collections'] += 1
        
        # Update average duration
        total_collections = self.collection_stats['total_collections']
        current_avg = self.collection_stats['avg_collection_duration']
        self.collection_stats['avg_collection_duration'] = (
            (current_avg * (total_collections - 1) + duration) / total_collections
        )
    
    def record_database_operation(self, operation: str, duration: float, success: bool = True):
        """Registra operação de database para monitoramento"""
        self.metrics_collector.record_operation(operation, duration, success)
        
        # Log operações muito lentas
        if duration > 30.0:
            self.logger.warning(f"Operação lenta detectada: {operation} levou {duration:.2f}s")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados completos para dashboard"""
        # Métricas recentes (últimos 5 minutos)
        recent_metrics = {}
        metric_names = [
            'cpu_usage', 'memory_usage', 'disk_usage',
            'mysql_connections', 'mysql_qps', 'mysql_buffer_pool_usage',
            'save_products_duration', 'save_restaurants_duration', 'save_categories_duration'
        ]
        
        for metric_name in metric_names:
            stats = self.metrics_collector.get_metric_stats(metric_name, window_minutes=5)
            if stats:
                recent_metrics[metric_name] = stats
        
        # Estatísticas de operações
        operation_stats = {}
        operations = ['save_products', 'save_restaurants', 'save_categories']
        for op in operations:
            stats = self.metrics_collector.get_operation_stats(op)
            if stats:
                operation_stats[op] = stats
        
        # Status de retry do sistema
        retry_status = get_retry_status()
        
        # Alertas
        active_alerts = self.alert_manager.get_active_alerts()
        recent_alerts = self.alert_manager.alert_history[-10:]  # Últimos 10
        alert_summary = self.alert_manager.get_alert_summary(hours=24)
        
        # Contadores de tabelas
        table_stats = {}
        for table in ['products', 'restaurants', 'categories']:
            metric_name = f'table_count_{table}'
            stats = self.metrics_collector.get_metric_stats(metric_name, window_minutes=60)
            if stats:
                table_stats[table] = stats['latest']
        
        # System information
        system_info = self.system_collector.get_system_info()
        mysql_info = self.mysql_collector.get_database_info()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': recent_metrics,
            'operation_stats': operation_stats,
            'retry_status': retry_status,
            'active_alerts': active_alerts,
            'recent_alerts': recent_alerts,
            'alert_summary': alert_summary,
            'table_stats': table_stats,
            'system_info': system_info,
            'mysql_info': mysql_info,
            'monitor_status': {
                'running': self.running,
                'collection_interval': self.collection_interval,
                'uptime_seconds': (datetime.now() - self.metrics_collector.start_time).total_seconds(),
                'collection_stats': self.collection_stats
            },
            'collector_stats': self.metrics_collector.get_collector_stats()
        }
    
    def get_historical_data(self, metric_names: List[str], hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna dados históricos para métricas específicas"""
        historical_data = {}
        
        for metric_name in metric_names:
            # Get all metrics for this name in the time window
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            metric_history = self.metrics_collector.metrics_history.get(metric_name, [])
            recent_metrics = [
                m.to_dict() for m in metric_history 
                if m.timestamp >= cutoff_time
            ]
            
            if recent_metrics:
                historical_data[metric_name] = recent_metrics
        
        return historical_data
    
    def export_metrics(self, format: str = 'json', window_hours: int = 1) -> str:
        """Exporta métricas em formato especificado"""
        exported_data = {
            'export_timestamp': datetime.now().isoformat(),
            'window_hours': window_hours,
            'monitor_info': {
                'collection_interval': self.collection_interval,
                'collection_stats': self.collection_stats,
                'system_info': self.system_collector.get_system_info(),
                'mysql_info': self.mysql_collector.get_database_info()
            },
            'metrics': self.metrics_collector.get_all_metrics(window_hours),
            'alert_summary': self.alert_manager.get_alert_summary(window_hours),
            'recent_alerts': [
                alert for alert in self.alert_manager.alert_history
                if datetime.fromisoformat(alert['timestamp']) >= 
                   datetime.now() - timedelta(hours=window_hours)
            ]
        }
        
        if format.lower() == 'json':
            return json.dumps(exported_data, indent=2, default=str)
        else:
            # Could add CSV or other formats here
            return str(exported_data)
    
    def cleanup_old_data(self, hours_to_keep: int = 24):
        """Remove dados antigos para economizar memória"""
        self.logger.info(f"Iniciando limpeza de dados antigos (mantendo {hours_to_keep}h)")
        
        # Clean metrics
        self.metrics_collector.clear_old_metrics(hours_to_keep)
        
        # Clean alert history
        cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
        initial_count = len(self.alert_manager.alert_history)
        
        self.alert_manager.alert_history = [
            alert for alert in self.alert_manager.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]
        
        cleaned_alerts = initial_count - len(self.alert_manager.alert_history)
        self.logger.info(f"Limpeza concluída: {cleaned_alerts} alertas antigos removidos")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do monitor"""
        return {
            'running': self.running,
            'collection_interval': self.collection_interval,
            'uptime_seconds': (datetime.now() - self.metrics_collector.start_time).total_seconds(),
            'collection_stats': self.collection_stats,
            'mysql_connection': self.mysql_collector.test_connection(),
            'total_metrics': sum(len(history) for history in self.metrics_collector.metrics_history.values()),
            'active_alerts': len(self.alert_manager.active_alerts),
            'total_rules': len(self.alert_manager.rules)
        }
    
    def force_collection(self) -> Dict[str, Any]:
        """Força uma coleta imediata de métricas"""
        self.logger.info("Forçando coleta imediata de métricas")
        
        start_time = time.time()
        try:
            all_metrics = self._collect_all_metrics()
            
            # Register metrics
            for metric in all_metrics:
                self.metrics_collector.record_metric(metric)
            
            # Check alerts
            self.alert_manager.check_alerts(all_metrics)
            
            duration = time.time() - start_time
            
            return {
                'success': True,
                'metrics_collected': len(all_metrics),
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Erro na coleta forçada: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }


# Export the monitor
__all__ = ['PerformanceMonitor']