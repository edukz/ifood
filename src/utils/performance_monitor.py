"""
Performance Monitor - Interface unificada para sistema modular de monitoramento
Refatorado para usar arquitetura modular v3.0
"""

# Import the modular performance system
from .performance import (
    PerformanceMonitor as ModularPerformanceMonitor,
    PerformanceMetric,
    AlertRule,
    performance_monitor,
    monitor_performance,
    monitor_database_operation,
    monitor_scraping_operation,
    monitor_api_call,
    performance_context
)

from src.utils.logger import setup_logger

logger = setup_logger("PerformanceMonitor")

# Models are now imported from the modular system
# PerformanceMetric and AlertRule are available via imports above

# PerformanceCollector functionality is now handled by multiple specialized collectors:
# - MetricsCollector: Base metrics storage and operation tracking
# - SystemCollector: System metrics (CPU, memory, disk)
# - MySQLCollector: MySQL-specific metrics
# All available via the modular performance system

# AlertManager functionality is now handled by the specialized AlertManager class
# in the modular performance system with enhanced features and better alerting

# Legacy PerformanceMonitor class - now delegates to the modular system
class LegacyPerformanceMonitor:
    """Legacy wrapper for backward compatibility"""
    
    def __init__(self, collection_interval: int = 60):
        self.monitor = ModularPerformanceMonitor(collection_interval)
        self.logger = logger
    
    def start(self):
        """Inicia monitoramento"""
        self.monitor.start()
    
    def stop(self):
        """Para monitoramento"""
        self.monitor.stop()
    
    def record_database_operation(self, operation: str, duration: float, success: bool = True):
        """Registra operação de database"""
        self.monitor.record_database_operation(operation, duration, success)
    
    def get_dashboard_data(self) -> dict:
        """Retorna dados para dashboard"""
        return self.monitor.get_dashboard_data()
    
    def export_metrics(self, format: str = 'json', window_hours: int = 1) -> str:
        """Exporta métricas em formato especificado"""
        return self.monitor.export_metrics(format, window_hours)
    
    @property
    def running(self) -> bool:
        """Status do monitor"""
        return self.monitor.running
    
    @property
    def collection_interval(self) -> int:
        """Intervalo de coleta"""
        return self.monitor.collection_interval

# Legacy compatibility - use the global instance from the modular system
# but provide backward compatibility for existing code
class PerformanceMonitorCompat(LegacyPerformanceMonitor):
    """Backward compatibility wrapper"""
    pass

# For backward compatibility, provide the old interface
PerformanceMonitor = PerformanceMonitorCompat

# Export the backward-compatible interface and new modular system
__all__ = [
    # Backward compatibility
    'PerformanceMonitor',
    'PerformanceMetric', 
    'AlertRule',
    'monitor_performance',
    
    # New modular system (recommended)
    'performance_monitor',
    'monitor_database_operation', 
    'monitor_scraping_operation',
    'monitor_api_call',
    'performance_context'
]


if __name__ == "__main__":
    # Teste do sistema modular de monitoramento
    print("🔍 Testando sistema modular de monitoramento...")
    
    # Use the global monitor instance
    monitor = performance_monitor
    monitor.start()
    
    # Test decorators
    @monitor_database_operation("test_save")
    def test_operation():
        import time
        import random
        time.sleep(random.uniform(0.1, 1.0))
        return "success"
    
    # Test operations
    for i in range(5):
        try:
            result = test_operation()
            print(f"Operação {i+1}: {result}")
        except Exception as e:
            print(f"Erro na operação {i+1}: {e}")
    
    # Force collection
    collection_result = monitor.force_collection()
    print(f"\n📊 Coleta forçada: {collection_result}")
    
    # Get dashboard data
    dashboard = monitor.get_dashboard_data()
    print(f"\n📈 Métricas do sistema: {len(dashboard['system_metrics'])} tipos")
    print(f"📊 Alertas ativos: {len(dashboard['active_alerts'])}")
    print(f"🔄 Status do monitor: {dashboard['monitor_status']['running']}")
    
    monitor.stop()
    print("\n✅ Teste do sistema modular concluído!")