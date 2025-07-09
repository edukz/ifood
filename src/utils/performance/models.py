#!/usr/bin/env python3
"""
Performance Models - Data models for performance monitoring
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field


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
        """Convert to dictionary for serialization"""
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


# Export models
__all__ = ['PerformanceMetric', 'AlertRule']