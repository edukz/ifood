#!/usr/bin/env python3
"""
System Collector - System metrics collection (CPU, memory, disk, processes)
"""

import psutil
from typing import List
from datetime import datetime

from .models import PerformanceMetric
from src.utils.logger import setup_logger

logger = setup_logger("SystemCollector")


class SystemCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.logger = logger
    
    def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Coleta métricas do sistema"""
        now = datetime.now()
        metrics = []
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(PerformanceMetric(
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=now,
                category="system"
            ))
            
            # CPU per core
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            for i, cpu_core in enumerate(cpu_per_core):
                metrics.append(PerformanceMetric(
                    name=f"cpu_core_{i}_usage",
                    value=cpu_core,
                    unit="percent",
                    timestamp=now,
                    category="system",
                    metadata={'core': i}
                ))
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de CPU: {e}")
        
        try:
            # Memória
            memory = psutil.virtual_memory()
            
            metrics.append(PerformanceMetric(
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=now,
                category="system"
            ))
            
            metrics.append(PerformanceMetric(
                name="memory_available",
                value=memory.available / (1024**3),  # GB
                unit="GB",
                timestamp=now,
                category="system"
            ))
            
            metrics.append(PerformanceMetric(
                name="memory_used",
                value=memory.used / (1024**3),  # GB
                unit="GB",
                timestamp=now,
                category="system"
            ))
            
            metrics.append(PerformanceMetric(
                name="memory_total",
                value=memory.total / (1024**3),  # GB
                unit="GB",
                timestamp=now,
                category="system"
            ))
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de memória: {e}")
        
        try:
            # Swap
            swap = psutil.swap_memory()
            if swap.total > 0:
                metrics.append(PerformanceMetric(
                    name="swap_usage",
                    value=swap.percent,
                    unit="percent",
                    timestamp=now,
                    category="system"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de swap: {e}")
        
        try:
            # Disco - root partition
            disk = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                name="disk_usage",
                value=disk.percent,
                unit="percent",
                timestamp=now,
                category="system"
            ))
            
            metrics.append(PerformanceMetric(
                name="disk_free",
                value=disk.free / (1024**3),  # GB
                unit="GB",
                timestamp=now,
                category="system"
            ))
            
            metrics.append(PerformanceMetric(
                name="disk_total",
                value=disk.total / (1024**3),  # GB
                unit="GB",
                timestamp=now,
                category="system"
            ))
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de disco: {e}")
        
        try:
            # I/O de disco
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.append(PerformanceMetric(
                    name="disk_read_bytes",
                    value=disk_io.read_bytes / (1024**2),  # MB
                    unit="MB",
                    timestamp=now,
                    category="system"
                ))
                
                metrics.append(PerformanceMetric(
                    name="disk_write_bytes",
                    value=disk_io.write_bytes / (1024**2),  # MB
                    unit="MB",
                    timestamp=now,
                    category="system"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de I/O de disco: {e}")
        
        try:
            # Processos
            process_count = len(psutil.pids())
            metrics.append(PerformanceMetric(
                name="process_count",
                value=process_count,
                unit="count",
                timestamp=now,
                category="system"
            ))
            
            # Load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
                for i, load in enumerate(load_avg):
                    period = ['1min', '5min', '15min'][i]
                    metrics.append(PerformanceMetric(
                        name=f"load_avg_{period}",
                        value=load,
                        unit="load",
                        timestamp=now,
                        category="system",
                        metadata={'period': period}
                    ))
            except (AttributeError, OSError):
                # getloadavg not available on Windows
                pass
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de processos: {e}")
        
        try:
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.append(PerformanceMetric(
                    name="network_bytes_sent",
                    value=net_io.bytes_sent / (1024**2),  # MB
                    unit="MB",
                    timestamp=now,
                    category="system"
                ))
                
                metrics.append(PerformanceMetric(
                    name="network_bytes_recv",
                    value=net_io.bytes_recv / (1024**2),  # MB
                    unit="MB",
                    timestamp=now,
                    category="system"
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de rede: {e}")
        
        return metrics
    
    def get_system_info(self) -> dict:
        """Retorna informações estáticas do sistema"""
        try:
            info = {
                'platform': psutil.LINUX if hasattr(psutil, 'LINUX') else 'unknown',
                'cpu_count_logical': psutil.cpu_count(),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'python_version': psutil.version_info if hasattr(psutil, 'version_info') else 'unknown'
            }
            
            # CPU info
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    info['cpu_freq_current'] = cpu_freq.current
                    info['cpu_freq_min'] = cpu_freq.min
                    info['cpu_freq_max'] = cpu_freq.max
            except:
                pass
            
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}


# Export the collector
__all__ = ['SystemCollector']