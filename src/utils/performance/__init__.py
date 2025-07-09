#!/usr/bin/env python3
"""
Performance Module - Modular performance monitoring system
"""

# Core models
from .models import PerformanceMetric, AlertRule

# Collectors
from .metrics_collector import MetricsCollector
from .system_collector import SystemCollector
from .mysql_collector import MySQLCollector

# Alert management
from .alert_manager import AlertManager

# Main monitor
from .monitor import PerformanceMonitor

# Decorators and utilities
from .decorators import (
    set_global_monitor,
    monitor_performance,
    monitor_database_operation,
    monitor_scraping_operation,
    monitor_api_call,
    performance_context,
    get_monitor_status,
    force_collection
)

# Create a global monitor instance
performance_monitor = PerformanceMonitor()

# Set global monitor for decorators
set_global_monitor(performance_monitor)

# Export all public components
__all__ = [
    # Models
    'PerformanceMetric',
    'AlertRule',
    
    # Collectors
    'MetricsCollector',
    'SystemCollector', 
    'MySQLCollector',
    
    # Alert management
    'AlertManager',
    
    # Main monitor
    'PerformanceMonitor',
    'performance_monitor',  # Global instance
    
    # Decorators
    'set_global_monitor',
    'monitor_performance',
    'monitor_database_operation',
    'monitor_scraping_operation',
    'monitor_api_call',
    'performance_context',
    'get_monitor_status',
    'force_collection'
]

__version__ = '3.0.0'
__description__ = 'Modular performance monitoring system for iFood scraper'