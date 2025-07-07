"""
Sistema robusto de retry para operações MySQL
Inclui exponential backoff, jitter e circuit breaker
"""

import time
import random
import functools
from typing import Callable, Type, Union, Tuple, Any, Optional
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error as MySQLError

from src.utils.logger import setup_logger

logger = setup_logger("RetryHandler")


class RetryError(Exception):
    """Erro após esgotar todas as tentativas"""
    pass


class CircuitBreakerError(Exception):
    """Erro quando circuit breaker está aberto"""
    pass


class RetryConfig:
    """Configuração de retry"""
    
    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_factor: float = 2.0,
                 jitter: bool = True,
                 jitter_factor: float = 0.1):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.jitter_factor = jitter_factor
    
    def calculate_delay(self, attempt: int) -> float:
        """Calcula delay para uma tentativa específica"""
        # Exponential backoff
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        
        # Limita delay máximo
        delay = min(delay, self.max_delay)
        
        # Adiciona jitter para evitar thundering herd
        if self.jitter:
            jitter_amount = delay * self.jitter_factor
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)


class CircuitBreaker:
    """Circuit breaker para evitar tentativas desnecessárias"""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 timeout: float = 60.0,
                 success_threshold: int = 2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'closed'  # closed, open, half-open
    
    def can_execute(self) -> bool:
        """Verifica se pode executar operação"""
        if self.state == 'closed':
            return True
        
        if self.state == 'open':
            # Verifica se deve tentar half-open
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)):
                self.state = 'half-open'
                self.success_count = 0
                logger.info("🔄 Circuit breaker: open → half-open")
                return True
            return False
        
        if self.state == 'half-open':
            return True
        
        return False
    
    def record_success(self):
        """Registra sucesso"""
        if self.state == 'half-open':
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = 'closed'
                self.failure_count = 0
                logger.info("✅ Circuit breaker: half-open → closed")
        elif self.state == 'closed':
            self.failure_count = 0
    
    def record_failure(self):
        """Registra falha"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == 'closed' and self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"🚨 Circuit breaker opened após {self.failure_count} falhas")
        elif self.state == 'half-open':
            self.state = 'open'
            logger.warning("🚨 Circuit breaker: half-open → open")


def classify_mysql_error(error: MySQLError) -> str:
    """Classifica erro MySQL para determinar estratégia"""
    error_code = error.errno
    error_msg = str(error).lower()
    
    # Erros temporários (deve tentar novamente)
    if error_code in [
        2003,  # Can't connect to MySQL server
        2006,  # MySQL server has gone away
        2013,  # Lost connection to MySQL server
        1040,  # Too many connections
        1205,  # Lock wait timeout exceeded
        1213,  # Deadlock found when trying to get lock
        1020,  # Record has changed since last read
    ]:
        return 'temporary'
    
    # Erros de conexão
    if any(keyword in error_msg for keyword in [
        'connection', 'timeout', 'broken pipe', 'reset by peer'
    ]):
        return 'connection'
    
    # Erros permanentes (não deve tentar novamente)
    if error_code in [
        1044,  # Access denied for user
        1045,  # Access denied for user (using password)
        1049,  # Unknown database
        1146,  # Table doesn't exist
        1054,  # Unknown column
        1064,  # SQL syntax error
    ]:
        return 'permanent'
    
    # Por padrão, trata como temporário
    return 'temporary'


def retry_mysql_operation(
    config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    retry_on: Tuple[Type[Exception], ...] = (MySQLError,)
):
    """
    Decorator para retry de operações MySQL
    
    Args:
        config: Configuração de retry
        circuit_breaker: Circuit breaker (opcional)
        retry_on: Tupla de exceções que devem causar retry
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verifica circuit breaker
            if circuit_breaker and not circuit_breaker.can_execute():
                raise CircuitBreakerError(
                    f"Circuit breaker está aberto para {func.__name__}"
                )
            
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Sucesso - registra no circuit breaker
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    # Log sucesso após retry
                    if attempt > 1:
                        logger.info(f"✅ {func.__name__} sucesso na tentativa {attempt}")
                    
                    return result
                
                except retry_on as e:
                    last_exception = e
                    
                    # Para erros MySQL, verifica se deve tentar novamente
                    if isinstance(e, MySQLError):
                        error_type = classify_mysql_error(e)
                        if error_type == 'permanent':
                            logger.error(f"❌ Erro permanente em {func.__name__}: {e}")
                            if circuit_breaker:
                                circuit_breaker.record_failure()
                            raise e
                    
                    # Se é a última tentativa, não faz delay
                    if attempt == config.max_attempts:
                        break
                    
                    # Calcula delay e aguarda
                    delay = config.calculate_delay(attempt)
                    
                    logger.warning(
                        f"⚠️ {func.__name__} falhou (tentativa {attempt}/{config.max_attempts}): {e}"
                    )
                    logger.info(f"⏳ Aguardando {delay:.2f}s antes da próxima tentativa...")
                    
                    time.sleep(delay)
                
                except Exception as e:
                    # Exceções não relacionadas a retry
                    logger.error(f"❌ Erro não recuperável em {func.__name__}: {e}")
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    raise e
            
            # Todas as tentativas falharam
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            logger.error(
                f"❌ {func.__name__} falhou após {config.max_attempts} tentativas"
            )
            raise RetryError(
                f"Operação {func.__name__} falhou após {config.max_attempts} tentativas. "
                f"Último erro: {last_exception}"
            )
        
        return wrapper
    return decorator


class MySQLRetryManager:
    """Gerenciador de retry para operações MySQL"""
    
    def __init__(self,
                 connection_config: Optional[RetryConfig] = None,
                 operation_config: Optional[RetryConfig] = None,
                 enable_circuit_breaker: bool = True):
        
        # Configurações específicas
        self.connection_config = connection_config or RetryConfig(
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0
        )
        
        self.operation_config = operation_config or RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            max_delay=10.0,
            backoff_factor=1.5
        )
        
        # Circuit breakers
        self.connection_breaker = CircuitBreaker() if enable_circuit_breaker else None
        self.operation_breaker = CircuitBreaker(
            failure_threshold=10,
            timeout=120.0
        ) if enable_circuit_breaker else None
    
    def retry_connection(self, func: Callable) -> Callable:
        """Decorator para retry de conexões"""
        return retry_mysql_operation(
            config=self.connection_config,
            circuit_breaker=self.connection_breaker,
            retry_on=(MySQLError, ConnectionError, TimeoutError)
        )(func)
    
    def retry_operation(self, func: Callable) -> Callable:
        """Decorator para retry de operações"""
        return retry_mysql_operation(
            config=self.operation_config,
            circuit_breaker=self.operation_breaker,
            retry_on=(MySQLError,)
        )(func)
    
    def get_status(self) -> dict:
        """Retorna status dos circuit breakers"""
        status = {}
        
        if self.connection_breaker:
            status['connection_breaker'] = {
                'state': self.connection_breaker.state,
                'failure_count': self.connection_breaker.failure_count,
                'last_failure': self.connection_breaker.last_failure_time
            }
        
        if self.operation_breaker:
            status['operation_breaker'] = {
                'state': self.operation_breaker.state,
                'failure_count': self.operation_breaker.failure_count,
                'last_failure': self.operation_breaker.last_failure_time
            }
        
        return status


# Instância global para uso fácil
mysql_retry_manager = MySQLRetryManager()

# Shortcuts para decorators comuns
retry_connection = mysql_retry_manager.retry_connection
retry_operation = mysql_retry_manager.retry_operation

# Configurações pré-definidas
AGGRESSIVE_RETRY = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    backoff_factor=2.0
)

CONSERVATIVE_RETRY = RetryConfig(
    max_attempts=2,
    base_delay=2.0,
    max_delay=10.0,
    backoff_factor=1.5
)

PATIENT_RETRY = RetryConfig(
    max_attempts=10,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=1.3
)


if __name__ == "__main__":
    # Teste do sistema de retry
    
    @retry_operation
    def test_function(should_fail: bool = False):
        """Função de teste"""
        if should_fail:
            raise MySQLError("Teste de erro", 2006)  # MySQL server has gone away
        return "Sucesso!"
    
    # Teste de sucesso
    print("Testando sucesso:")
    result = test_function(False)
    print(f"Resultado: {result}")
    
    # Teste de falha e retry
    print("\nTestando retry:")
    try:
        result = test_function(True)
    except RetryError as e:
        print(f"Falhou como esperado: {e}")
    
    # Status dos circuit breakers
    print(f"\nStatus: {mysql_retry_manager.get_status()}")