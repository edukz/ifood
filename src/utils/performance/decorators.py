#!/usr/bin/env python3
"""
Performance Decorators - Decorators for automatic performance monitoring
"""

import time
import functools
from typing import Optional, Callable, Any

from src.utils.logger import setup_logger

logger = setup_logger("PerformanceDecorators")

# Global monitor instance (will be set by the main monitor)
_global_monitor: Optional['PerformanceMonitor'] = None


def set_global_monitor(monitor: 'PerformanceMonitor'):
    """Set the global monitor instance for decorators"""
    global _global_monitor
    _global_monitor = monitor
    logger.info("Global performance monitor configurado para decorators")


def monitor_performance(operation_name: str):
    """
    Decorator para monitorar performance de operações automaticamente
    
    Usage:
        @monitor_performance("database_save")
        def save_data():
            # function code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                logger.error(f"Erro em operação monitorada '{operation_name}': {e}")
                raise
                
            finally:
                duration = time.time() - start_time
                
                # Record to global monitor if available
                if _global_monitor:
                    _global_monitor.record_database_operation(operation_name, duration, success)
                
                # Log slow operations
                if duration > 10.0:  # Log operations taking more than 10 seconds
                    log_level = "warning" if success else "error"
                    getattr(logger, log_level)(
                        f"Operação '{operation_name}' levou {duration:.2f}s "
                        f"({'sucesso' if success else 'falha'})"
                    )
        
        return wrapper
    return decorator


def monitor_database_operation(operation_name: Optional[str] = None):
    """
    Decorator específico para operações de banco de dados
    Se operation_name não for especificado, usa o nome da função
    """
    def decorator(func: Callable) -> Callable:
        actual_operation_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                logger.error(f"Erro na operação de banco '{actual_operation_name}': {e}")
                raise
                
            finally:
                duration = time.time() - start_time
                
                if _global_monitor:
                    _global_monitor.record_database_operation(actual_operation_name, duration, success)
                
                # Log very slow database operations
                if duration > 30.0:
                    log_level = "error" if duration > 60.0 else "warning"
                    getattr(logger, log_level)(
                        f"Operação de banco '{actual_operation_name}' muito lenta: {duration:.2f}s"
                    )
        
        return wrapper
    return decorator


def monitor_scraping_operation(operation_type: str):
    """
    Decorator específico para operações de scraping
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            items_processed = 0
            
            try:
                result = func(*args, **kwargs)
                
                # Try to extract number of items processed from result
                if isinstance(result, (list, tuple)):
                    items_processed = len(result)
                elif isinstance(result, dict) and 'count' in result:
                    items_processed = result['count']
                elif isinstance(result, int):
                    items_processed = result
                
                return result
                
            except Exception as e:
                success = False
                logger.error(f"Erro na operação de scraping '{operation_type}': {e}")
                raise
                
            finally:
                duration = time.time() - start_time
                
                if _global_monitor:
                    # Create specific metric name for scraping
                    metric_name = f"scraping_{operation_type}"
                    _global_monitor.record_database_operation(metric_name, duration, success)
                
                # Log scraping performance
                if items_processed > 0 and duration > 0:
                    rate = items_processed / duration
                    logger.info(
                        f"Scraping '{operation_type}': {items_processed} itens em {duration:.2f}s "
                        f"({rate:.2f} itens/s)"
                    )
                elif duration > 60.0:  # Log slow scraping operations
                    logger.warning(
                        f"Scraping '{operation_type}' lento: {duration:.2f}s"
                    )
        
        return wrapper
    return decorator


def monitor_api_call(api_name: str, timeout_warning: float = 5.0):
    """
    Decorator para monitorar chamadas de API
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                logger.error(f"Erro na chamada API '{api_name}': {e}")
                raise
                
            finally:
                duration = time.time() - start_time
                
                if _global_monitor:
                    # Create specific metric name for API calls
                    metric_name = f"api_call_{api_name}"
                    _global_monitor.record_database_operation(metric_name, duration, success)
                
                # Log slow API calls
                if duration > timeout_warning:
                    log_level = "warning" if duration < (timeout_warning * 2) else "error"
                    getattr(logger, log_level)(
                        f"API '{api_name}' lenta: {duration:.2f}s (threshold: {timeout_warning}s)"
                    )
        
        return wrapper
    return decorator


def performance_context(operation_name: str):
    """
    Context manager para monitorar blocos de código
    
    Usage:
        with performance_context("complex_calculation"):
            # code block
            pass
    """
    class PerformanceContext:
        def __init__(self, name: str):
            self.name = name
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            logger.debug(f"Iniciando monitoramento: {self.name}")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time is not None:
                duration = time.time() - self.start_time
                success = exc_type is None
                
                if _global_monitor:
                    _global_monitor.record_database_operation(self.name, duration, success)
                
                if not success:
                    logger.error(f"Erro no contexto '{self.name}': {exc_val}")
                elif duration > 10.0:
                    logger.warning(f"Contexto '{self.name}' lento: {duration:.2f}s")
                else:
                    logger.debug(f"Contexto '{self.name}' concluído: {duration:.2f}s")
    
    return PerformanceContext(operation_name)


# Convenience functions
def get_monitor_status() -> dict:
    """Retorna status do monitor global"""
    if _global_monitor:
        return _global_monitor.get_status()
    return {'status': 'no_monitor', 'message': 'No global monitor configured'}


def force_collection() -> dict:
    """Força coleta imediata no monitor global"""
    if _global_monitor:
        return _global_monitor.force_collection()
    return {'status': 'no_monitor', 'message': 'No global monitor configured'}


# Export all decorators and utilities
__all__ = [
    'set_global_monitor',
    'monitor_performance', 
    'monitor_database_operation',
    'monitor_scraping_operation',
    'monitor_api_call',
    'performance_context',
    'get_monitor_status',
    'force_collection'
]