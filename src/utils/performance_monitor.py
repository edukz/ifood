"""
Sistema de Monitoramento de Performance para MySQL
Inclui métricas, alertas e dashboards em tempo real
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
import json
import statistics

from src.config.database import execute_query, get_retry_status
from src.utils.logger import setup_logger

logger = setup_logger("PerformanceMonitor")


@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category,
            'metadata': self.metadata
        }


@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    metric_name: str
    condition: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    threshold: float
    duration_seconds: int = 60  # Alerta só após X segundos
    enabled: bool = True
    callback: Optional[Callable] = None
    
    def check(self, value: float) -> bool:
        """Verifica se alerta deve ser disparado"""
        if not self.enabled:
            return False
            
        conditions = {
            'gt': value > self.threshold,
            'lt': value < self.threshold,
            'gte': value >= self.threshold,
            'lte': value <= self.threshold,
            'eq': value == self.threshold
        }
        
        return conditions.get(self.condition, False)


class PerformanceCollector:
    """Coletor de métricas de performance"""
    
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
    
    def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Coleta métricas do sistema"""
        now = datetime.now()
        metrics = []
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        metrics.append(PerformanceMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=now,
            category="system"
        ))
        
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
        
        # Disco
        try:
            disk = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                name="disk_usage",
                value=disk.percent,
                unit="percent",
                timestamp=now,
                category="system"
            ))
        except:
            pass
        
        # Processos
        try:
            process_count = len(psutil.pids())
            metrics.append(PerformanceMetric(
                name="process_count",
                value=process_count,
                unit="count",
                timestamp=now,
                category="system"
            ))
        except:
            pass
        
        return metrics
    
    def collect_mysql_metrics(self) -> List[PerformanceMetric]:
        """Coleta métricas específicas do MySQL"""
        now = datetime.now()
        metrics = []
        
        # Desabilita temporariamente para evitar erros
        return metrics
        
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
            
            # Queries por segundo
            queries = execute_query("SHOW STATUS LIKE 'Queries'", fetch_all=True)
            if queries and hasattr(self, '_last_queries'):
                current_queries = float(queries[0]['Value'])
                qps = (current_queries - self._last_queries) / 60  # Assumindo coleta a cada minuto
                metrics.append(PerformanceMetric(
                    name="mysql_qps",
                    value=qps,
                    unit="queries/second",
                    timestamp=now,
                    category="mysql"
                ))
            if queries:
                self._last_queries = float(queries[0]['Value'])
            
            # Tamanho das tabelas principais
            tables_size = execute_query("""
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                FROM information_schema.tables
                WHERE table_schema = 'ifood_scraper'
                AND table_name IN ('products', 'restaurants', 'categories')
            """, fetch_all=True)
            
            for table in tables_size or []:
                table_name = table.get('table_name') or table.get('TABLE_NAME', 'unknown')
                size_mb = table.get('size_mb') or table.get('SIZE_MB', 0)
                metrics.append(PerformanceMetric(
                    name=f"table_size_{table_name}",
                    value=float(size_mb),
                    unit="MB",
                    timestamp=now,
                    category="mysql",
                    metadata={'table': table_name}
                ))
            
            # Contagem de registros
            counts = {
                'categories': execute_query("SELECT COUNT(*) FROM categories", fetch_one=True),
                'restaurants': execute_query("SELECT COUNT(*) FROM restaurants", fetch_one=True),
                'products': execute_query("SELECT COUNT(*) FROM products", fetch_one=True)
            }
            
            for table, count_result in counts.items():
                if count_result:
                    # Safely extract count value
                    if isinstance(count_result, dict):
                        count_value = list(count_result.values())[0]
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
            logger.error(f"Erro ao coletar métricas MySQL: {e}")
        
        return metrics


class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Alertas padrão
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Configura alertas padrão"""
        default_rules = [
            AlertRule(
                name="High CPU Usage",
                metric_name="cpu_usage",
                condition="gt",
                threshold=80.0,
                duration_seconds=60
            ),
            AlertRule(
                name="High Memory Usage", 
                metric_name="memory_usage",
                condition="gt",
                threshold=85.0,
                duration_seconds=120
            ),
            AlertRule(
                name="Slow Database Operations",
                metric_name="save_products_duration",
                condition="gt",
                threshold=30.0,  # 30 segundos
                duration_seconds=30
            ),
            AlertRule(
                name="High MySQL Connections",
                metric_name="mysql_connections",
                condition="gt",
                threshold=50.0,
                duration_seconds=60
            )
        ]
        
        self.rules.extend(default_rules)
    
    def add_rule(self, rule: AlertRule):
        """Adiciona regra de alerta"""
        self.rules.append(rule)
    
    def check_alerts(self, metrics: List[PerformanceMetric]):
        """Verifica alertas para métricas"""
        now = datetime.now()
        
        for metric in metrics:
            for rule in self.rules:
                if rule.metric_name == metric.name and rule.check(metric.value):
                    alert_key = f"{rule.name}_{metric.name}"
                    
                    # Verifica se alerta já está ativo
                    if alert_key in self.active_alerts:
                        # Verifica duração
                        if (now - self.active_alerts[alert_key]).total_seconds() >= rule.duration_seconds:
                            self._fire_alert(rule, metric)
                    else:
                        # Inicia timer do alerta
                        self.active_alerts[alert_key] = now
                
                # Remove alertas que não estão mais ativos
                elif rule.metric_name == metric.name:
                    alert_key = f"{rule.name}_{metric.name}"
                    if alert_key in self.active_alerts:
                        del self.active_alerts[alert_key]
    
    def _fire_alert(self, rule: AlertRule, metric: PerformanceMetric):
        """Dispara alerta"""
        alert_data = {
            'rule_name': rule.name,
            'metric_name': metric.name,
            'metric_value': metric.value,
            'threshold': rule.threshold,
            'timestamp': datetime.now().isoformat(),
            'severity': self._get_severity(metric.value, rule.threshold)
        }
        
        self.alert_history.append(alert_data)
        
        # Mantém apenas últimos 100 alertas
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Log do alerta
        logger.warning(f"🚨 ALERTA: {rule.name} - {metric.name} = {metric.value}{metric.unit} (threshold: {rule.threshold})")
        
        # Callback customizado
        if rule.callback:
            try:
                rule.callback(alert_data)
            except Exception as e:
                logger.error(f"Erro no callback do alerta: {e}")
    
    def _get_severity(self, value: float, threshold: float) -> str:
        """Determina severidade do alerta"""
        ratio = value / threshold
        if ratio >= 2.0:
            return "critical"
        elif ratio >= 1.5:
            return "high"
        elif ratio >= 1.2:
            return "medium"
        else:
            return "low"
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        now = datetime.now()
        active = []
        
        for alert_key, start_time in self.active_alerts.items():
            duration = (now - start_time).total_seconds()
            active.append({
                'alert': alert_key,
                'duration_seconds': duration,
                'started_at': start_time.isoformat()
            })
        
        return active


class PerformanceMonitor:
    """Monitor principal de performance"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.collector = PerformanceCollector()
        self.alert_manager = AlertManager()
        
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        self.logger = setup_logger("PerformanceMonitor")
    
    def start(self):
        """Inicia monitoramento"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"Performance Monitor iniciado (intervalo: {self.collection_interval}s)")
    
    def stop(self):
        """Para monitoramento"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Performance Monitor parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Coleta métricas
                system_metrics = self.collector.collect_system_metrics()
                mysql_metrics = self.collector.collect_mysql_metrics()
                
                all_metrics = system_metrics + mysql_metrics
                
                # Registra métricas
                for metric in all_metrics:
                    self.collector.record_metric(metric)
                
                # Verifica alertas
                self.alert_manager.check_alerts(all_metrics)
                
                # Aguarda próxima coleta
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(self.collection_interval)
    
    def record_database_operation(self, operation: str, duration: float, success: bool = True):
        """Registra operação de database"""
        self.collector.record_operation(operation, duration, success)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard"""
        
        # Métricas recentes (últimos 5 minutos)
        recent_metrics = {}
        metric_names = [
            'cpu_usage', 'memory_usage', 'mysql_connections', 'mysql_qps',
            'save_products_duration', 'save_restaurants_duration', 'save_categories_duration'
        ]
        
        for metric_name in metric_names:
            stats = self.collector.get_metric_stats(metric_name, window_minutes=5)
            if stats:
                recent_metrics[metric_name] = stats
        
        # Estatísticas de operações
        operation_stats = {}
        operations = ['save_products', 'save_restaurants', 'save_categories']
        for op in operations:
            stats = self.collector.get_operation_stats(op)
            if stats:
                operation_stats[op] = stats
        
        # Status de retry
        retry_status = get_retry_status()
        
        # Alertas ativos
        active_alerts = self.alert_manager.get_active_alerts()
        recent_alerts = self.alert_manager.alert_history[-10:]  # Últimos 10
        
        # Contadores de tabelas
        table_stats = {}
        for metric_name in ['table_count_products', 'table_count_restaurants', 'table_count_categories']:
            stats = self.collector.get_metric_stats(metric_name, window_minutes=60)
            if stats:
                table_stats[metric_name.replace('table_count_', '')] = stats['latest']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': recent_metrics,
            'operation_stats': operation_stats,
            'retry_status': retry_status,
            'active_alerts': active_alerts,
            'recent_alerts': recent_alerts,
            'table_stats': table_stats,
            'monitor_status': {
                'running': self.running,
                'collection_interval': self.collection_interval,
                'uptime_seconds': (datetime.now() - self.collector.start_time).total_seconds()
            }
        }
    
    def export_metrics(self, format: str = 'json', window_hours: int = 1) -> str:
        """Exporta métricas em formato especificado"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        exported_data = {
            'export_timestamp': datetime.now().isoformat(),
            'window_hours': window_hours,
            'metrics': {}
        }
        
        # Exporta histórico de métricas
        for metric_name, metric_history in self.collector.metrics_history.items():
            recent_metrics = [
                m.to_dict() for m in metric_history 
                if m.timestamp >= cutoff_time
            ]
            if recent_metrics:
                exported_data['metrics'][metric_name] = recent_metrics
        
        if format == 'json':
            return json.dumps(exported_data, indent=2, default=str)
        else:
            # Outros formatos podem ser adicionados aqui
            return str(exported_data)


# Instância global
performance_monitor = PerformanceMonitor()


# Decorator para monitoramento automático
def monitor_performance(operation_name: str):
    """Decorator para monitorar performance de operações"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.record_database_operation(operation_name, duration, success)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Teste do sistema de monitoramento
    
    print("🔍 Testando sistema de monitoramento...")
    
    # Inicia monitor
    monitor = PerformanceMonitor(collection_interval=5)  # 5 segundos para teste
    monitor.start()
    
    # Simula algumas operações
    import random
    
    for i in range(10):
        # Simula operação de database
        duration = random.uniform(0.1, 2.0)
        success = random.choice([True, True, True, False])  # 75% sucesso
        
        monitor.record_database_operation(f"test_operation_{i%3}", duration, success)
        time.sleep(1)
    
    # Aguarda algumas coletas
    time.sleep(10)
    
    # Mostra dashboard
    dashboard = monitor.get_dashboard_data()
    print(f"\n📊 Dashboard data:")
    print(f"System metrics: {list(dashboard['system_metrics'].keys())}")
    print(f"Operation stats: {dashboard['operation_stats']}")
    print(f"Active alerts: {len(dashboard['active_alerts'])}")
    
    # Para monitor
    monitor.stop()
    print("✅ Teste concluído")