#!/usr/bin/env python3
"""
Metrics Collector - Base metrics collection and storage
"""

import threading
import statistics
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import deque, defaultdict

from .models import PerformanceMetric


class MetricsCollector:
    """Coletor base de métricas de performance"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.start_time = datetime.now()
        
        # Contadores específicos
        self.operation_counters = defaultdict(int)
        self.operation_timings = defaultdict(list)
        self.error_counts = defaultdict(int)
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    def record_metric(self, metric: PerformanceMetric):
        """Registra uma métrica"""
        with self._lock:
            self.metrics_history[metric.name].append(metric)
    
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Registra operação com timing"""
        with self._lock:
            self.operation_counters[operation] += 1
            self.operation_timings[operation].append(duration)
            
            # Mantém apenas últimos 100 timings por operação
            if len(self.operation_timings[operation]) > 100:
                self.operation_timings[operation] = self.operation_timings[operation][-100:]
            
            if not success:
                self.error_counts[operation] += 1
        
        # Cria métrica
        metric = PerformanceMetric(
            name=f"{operation}_duration",
            value=duration,
            unit="seconds",
            timestamp=datetime.now(),
            category="operation",
            metadata={'operation': operation, 'success': success}
        )
        self.record_metric(metric)
    
    def get_metric_stats(self, metric_name: str, window_minutes: int = 5) -> Dict[str, Any]:
        """Estatísticas de uma métrica"""
        with self._lock:
            if metric_name not in self.metrics_history:
                return {}
            
            # Filtra por janela de tempo
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_metrics = [
                m for m in self.metrics_history[metric_name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m.value for m in recent_metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values),
                'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                'latest': recent_metrics[-1].value,
                'window_minutes': window_minutes
            }
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Estatísticas de operação"""
        with self._lock:
            if operation not in self.operation_timings:
                return {}
            
            timings = self.operation_timings[operation]
            total_ops = self.operation_counters[operation]
            errors = self.error_counts[operation]
            
            return {
                'total_operations': total_ops,
                'error_count': errors,
                'success_rate': ((total_ops - errors) / total_ops * 100) if total_ops > 0 else 0,
                'avg_duration': statistics.mean(timings) if timings else 0,
                'min_duration': min(timings) if timings else 0,
                'max_duration': max(timings) if timings else 0,
                'p95_duration': statistics.quantiles(timings, n=20)[18] if len(timings) >= 20 else max(timings) if timings else 0,
                'operations_per_second': len(timings) / ((datetime.now() - self.start_time).total_seconds()) if timings else 0
            }
    
    def get_all_metrics(self, window_hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna todas as métricas em uma janela de tempo"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        all_metrics = {}
        with self._lock:
            for metric_name, metric_history in self.metrics_history.items():
                recent_metrics = [
                    m.to_dict() for m in metric_history 
                    if m.timestamp >= cutoff_time
                ]
                if recent_metrics:
                    all_metrics[metric_name] = recent_metrics
        
        return all_metrics
    
    def clear_old_metrics(self, hours_to_keep: int = 24):
        """Remove métricas antigas para economizar memória"""
        cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
        
        with self._lock:
            for metric_name in list(self.metrics_history.keys()):
                metric_history = self.metrics_history[metric_name]
                
                # Filtra métricas recentes
                recent_metrics = deque(
                    [m for m in metric_history if m.timestamp >= cutoff_time],
                    maxlen=self.max_history
                )
                
                if recent_metrics:
                    self.metrics_history[metric_name] = recent_metrics
                else:
                    # Remove histórico vazio
                    del self.metrics_history[metric_name]
    
    def get_collector_stats(self) -> Dict[str, Any]:
        """Estatísticas do coletor"""
        with self._lock:
            total_metrics = sum(len(history) for history in self.metrics_history.values())
            
            return {
                'total_metrics_stored': total_metrics,
                'unique_metric_names': len(self.metrics_history),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'total_operations_tracked': len(self.operation_counters),
                'memory_usage_estimate_mb': total_metrics * 0.001,  # Rough estimate
                'start_time': self.start_time.isoformat()
            }


# Export the collector
__all__ = ['MetricsCollector']