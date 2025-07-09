#!/usr/bin/env python3
"""
Alert Manager - Alert rules and notification management
"""

from typing import List, Dict, Any
from datetime import datetime

from .models import AlertRule, PerformanceMetric
from src.utils.logger import setup_logger

logger = setup_logger("AlertManager")


class AlertManager:
    """Gerenciador de alertas de performance"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.logger = logger
        
        # Alertas padrão
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Configura alertas padrão do sistema"""
        default_rules = [
            # System alerts
            AlertRule(
                name="High CPU Usage",
                metric_name="cpu_usage",
                condition="gt",
                threshold=80.0,
                duration_seconds=60
            ),
            AlertRule(
                name="Critical CPU Usage",
                metric_name="cpu_usage",
                condition="gt",
                threshold=95.0,
                duration_seconds=30
            ),
            AlertRule(
                name="High Memory Usage", 
                metric_name="memory_usage",
                condition="gt",
                threshold=85.0,
                duration_seconds=120
            ),
            AlertRule(
                name="Critical Memory Usage",
                metric_name="memory_usage",
                condition="gt",
                threshold=95.0,
                duration_seconds=60
            ),
            AlertRule(
                name="High Disk Usage",
                metric_name="disk_usage",
                condition="gt",
                threshold=90.0,
                duration_seconds=300  # 5 minutes
            ),
            AlertRule(
                name="Critical Disk Usage",
                metric_name="disk_usage",
                condition="gt",
                threshold=95.0,
                duration_seconds=120
            ),
            
            # Database operation alerts
            AlertRule(
                name="Slow Database Operations",
                metric_name="save_products_duration",
                condition="gt",
                threshold=30.0,  # 30 segundos
                duration_seconds=30
            ),
            AlertRule(
                name="Very Slow Database Operations",
                metric_name="save_products_duration",
                condition="gt",
                threshold=60.0,  # 1 minuto
                duration_seconds=15
            ),
            AlertRule(
                name="Slow Restaurant Save",
                metric_name="save_restaurants_duration",
                condition="gt",
                threshold=20.0,
                duration_seconds=30
            ),
            AlertRule(
                name="Slow Category Save",
                metric_name="save_categories_duration",
                condition="gt",
                threshold=10.0,
                duration_seconds=30
            ),
            
            # MySQL alerts
            AlertRule(
                name="High MySQL Connections",
                metric_name="mysql_connections",
                condition="gt",
                threshold=50.0,
                duration_seconds=60
            ),
            AlertRule(
                name="Critical MySQL Connections",
                metric_name="mysql_connections",
                condition="gt",
                threshold=80.0,
                duration_seconds=30
            ),
            AlertRule(
                name="Low MySQL QPS",
                metric_name="mysql_qps",
                condition="lt",
                threshold=1.0,
                duration_seconds=120
            ),
            AlertRule(
                name="High Buffer Pool Usage",
                metric_name="mysql_buffer_pool_usage",
                condition="gt",
                threshold=90.0,
                duration_seconds=300
            ),
            
            # System resource alerts
            AlertRule(
                name="Too Many Processes",
                metric_name="process_count",
                condition="gt",
                threshold=500.0,
                duration_seconds=180
            ),
            AlertRule(
                name="High Load Average",
                metric_name="load_avg_1min",
                condition="gt",
                threshold=4.0,
                duration_seconds=120
            )
        ]
        
        self.rules.extend(default_rules)
        self.logger.info(f"Configurados {len(default_rules)} alertas padrão")
    
    def add_rule(self, rule: AlertRule):
        """Adiciona regra de alerta personalizada"""
        self.rules.append(rule)
        self.logger.info(f"Adicionada regra de alerta: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove regra de alerta pelo nome"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                self.logger.info(f"Removida regra de alerta: {rule_name}")
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Ativa regra de alerta"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                self.logger.info(f"Ativada regra de alerta: {rule_name}")
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Desativa regra de alerta"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                self.logger.info(f"Desativada regra de alerta: {rule_name}")
                return True
        return False
    
    def check_alerts(self, metrics: List[PerformanceMetric]):
        """Verifica alertas para métricas fornecidas"""
        now = datetime.now()
        
        for metric in metrics:
            for rule in self.rules:
                if not rule.enabled:
                    continue
                    
                if rule.metric_name == metric.name and rule.check(metric.value):
                    alert_key = f"{rule.name}_{metric.name}"
                    
                    # Verifica se alerta já está ativo
                    if alert_key in self.active_alerts:
                        # Verifica duração
                        duration = (now - self.active_alerts[alert_key]).total_seconds()
                        if duration >= rule.duration_seconds:
                            self._fire_alert(rule, metric, duration)
                    else:
                        # Inicia timer do alerta
                        self.active_alerts[alert_key] = now
                        self.logger.debug(f"Iniciado timer para alerta: {alert_key}")
                
                # Remove alertas que não estão mais ativos
                elif rule.metric_name == metric.name:
                    alert_key = f"{rule.name}_{metric.name}"
                    if alert_key in self.active_alerts:
                        del self.active_alerts[alert_key]
                        self.logger.debug(f"Alerta resolvido: {alert_key}")
    
    def _fire_alert(self, rule: AlertRule, metric: PerformanceMetric, duration: float):
        """Dispara alerta"""
        severity = self._get_severity(metric.value, rule.threshold, rule.condition)
        
        alert_data = {
            'rule_name': rule.name,
            'metric_name': metric.name,
            'metric_value': metric.value,
            'metric_unit': metric.unit,
            'threshold': rule.threshold,
            'condition': rule.condition,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'duration_seconds': duration,
            'category': metric.category,
            'metadata': metric.metadata
        }
        
        self.alert_history.append(alert_data)
        
        # Mantém apenas últimos 100 alertas
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Log do alerta com diferentes níveis baseado na severidade
        severity_icons = {
            'low': '⚠️',
            'medium': '🔶',
            'high': '🔴',
            'critical': '🚨'
        }
        
        icon = severity_icons.get(severity, '⚠️')
        log_msg = f"{icon} ALERTA [{severity.upper()}]: {rule.name} - {metric.name} = {metric.value}{metric.unit} (threshold: {rule.threshold}, duration: {duration:.1f}s)"
        
        if severity in ['critical', 'high']:
            self.logger.error(log_msg)
        elif severity == 'medium':
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)
        
        # Callback customizado
        if rule.callback:
            try:
                rule.callback(alert_data)
            except Exception as e:
                self.logger.error(f"Erro no callback do alerta {rule.name}: {e}")
    
    def _get_severity(self, value: float, threshold: float, condition: str) -> str:
        """Determina severidade do alerta baseado no valor e threshold"""
        if condition in ['gt', 'gte']:
            ratio = value / threshold if threshold > 0 else float('inf')
        elif condition in ['lt', 'lte']:
            ratio = threshold / value if value > 0 else float('inf')
        else:  # eq
            ratio = 1.0 if value == threshold else 0.0
        
        if ratio >= 2.0:
            return "critical"
        elif ratio >= 1.5:
            return "high"
        elif ratio >= 1.2:
            return "medium"
        else:
            return "low"
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos com detalhes"""
        now = datetime.now()
        active = []
        
        for alert_key, start_time in self.active_alerts.items():
            duration = (now - start_time).total_seconds()
            
            # Encontra a regra correspondente
            rule_name = alert_key.split('_')[0]  # Simplified extraction
            rule = next((r for r in self.rules if r.name.startswith(rule_name)), None)
            
            active.append({
                'alert_key': alert_key,
                'duration_seconds': duration,
                'started_at': start_time.isoformat(),
                'rule_name': rule.name if rule else rule_name,
                'threshold_reached': duration >= (rule.duration_seconds if rule else 60),
                'severity_estimate': 'medium' if duration > 300 else 'low'
            })
        
        return active
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo de alertas das últimas N horas"""
        cutoff_time = datetime.now() - datetime.timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]
        
        # Agrupa por severidade
        by_severity = {}
        by_rule = {}
        
        for alert in recent_alerts:
            severity = alert['severity']
            rule_name = alert['rule_name']
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_rule[rule_name] = by_rule.get(rule_name, 0) + 1
        
        return {
            'total_alerts': len(recent_alerts),
            'by_severity': by_severity,
            'by_rule': by_rule,
            'active_alerts_count': len(self.active_alerts),
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules if r.enabled]),
            'window_hours': hours
        }
    
    def clear_alert_history(self):
        """Limpa histórico de alertas"""
        cleared_count = len(self.alert_history)
        self.alert_history.clear()
        self.logger.info(f"Histórico de alertas limpo: {cleared_count} alertas removidos")
    
    def get_rules_info(self) -> List[Dict[str, Any]]:
        """Retorna informações sobre todas as regras"""
        return [
            {
                'name': rule.name,
                'metric_name': rule.metric_name,
                'condition': rule.condition,
                'threshold': rule.threshold,
                'duration_seconds': rule.duration_seconds,
                'enabled': rule.enabled,
                'has_callback': rule.callback is not None
            }
            for rule in self.rules
        ]


# Export the alert manager
__all__ = ['AlertManager']