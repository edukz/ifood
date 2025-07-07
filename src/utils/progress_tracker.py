"""
Sistema de tracking de progresso para operações de banco de dados
"""

import time
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ProgressStats:
    """Estatísticas de progresso"""
    current: int
    total: int
    chunk_size: int
    elapsed_time: float
    estimated_total_time: float
    estimated_remaining_time: float
    rate: float
    percentage: float
    
    def __str__(self):
        return (f"Progresso: {self.current}/{self.total} ({self.percentage:.1f}%) "
                f"- {self.rate:.0f} itens/s - "
                f"Restante: {self._format_time(self.estimated_remaining_time)}")
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Formata tempo em formato legível"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class ProgressTracker:
    """Tracker de progresso para operações em lote"""
    
    def __init__(self, total_items: int, chunk_size: int, 
                 callback: Optional[Callable[[ProgressStats], None]] = None,
                 update_interval: float = 1.0):
        self.total_items = total_items
        self.chunk_size = chunk_size
        self.callback = callback
        self.update_interval = update_interval
        
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.processed_items = 0
        self.completed_chunks = 0
        
        # Histórico para cálculo de taxa
        self.rate_history = []
        self.max_history = 10
    
    def update(self, chunk_processed: int, extra_data: Optional[Dict[str, Any]] = None):
        """Atualiza progresso com chunk processado"""
        self.processed_items += chunk_processed
        self.completed_chunks += 1
        
        current_time = time.time()
        
        # Calcula taxa atual
        elapsed = current_time - self.start_time
        rate = self.processed_items / elapsed if elapsed > 0 else 0
        
        # Mantém histórico de taxa para suavização
        self.rate_history.append(rate)
        if len(self.rate_history) > self.max_history:
            self.rate_history.pop(0)
        
        # Taxa suavizada
        avg_rate = sum(self.rate_history) / len(self.rate_history)
        
        # Estimativas de tempo
        estimated_total = self.total_items / avg_rate if avg_rate > 0 else 0
        estimated_remaining = (self.total_items - self.processed_items) / avg_rate if avg_rate > 0 else 0
        
        # Percentual
        percentage = (self.processed_items / self.total_items) * 100
        
        # Cria objeto de estatísticas
        stats = ProgressStats(
            current=self.processed_items,
            total=self.total_items,
            chunk_size=self.chunk_size,
            elapsed_time=elapsed,
            estimated_total_time=estimated_total,
            estimated_remaining_time=estimated_remaining,
            rate=avg_rate,
            percentage=percentage
        )
        
        # Adiciona dados extras se fornecidos
        if extra_data:
            for key, value in extra_data.items():
                setattr(stats, key, value)
        
        # Chama callback se deve atualizar
        should_update = (
            current_time - self.last_update_time >= self.update_interval or
            self.processed_items >= self.total_items
        )
        
        if should_update and self.callback:
            self.callback(stats)
            self.last_update_time = current_time
        
        return stats
    
    def is_complete(self) -> bool:
        """Verifica se processamento está completo"""
        return self.processed_items >= self.total_items


class ConsoleProgressCallback:
    """Callback para mostrar progresso no console"""
    
    def __init__(self, show_bar: bool = True, bar_width: int = 40):
        self.show_bar = show_bar
        self.bar_width = bar_width
        self.last_length = 0
    
    def __call__(self, stats: ProgressStats):
        """Exibe progresso no console"""
        message = self._format_message(stats)
        
        # Limpa linha anterior
        if self.last_length > 0:
            print('\r' + ' ' * self.last_length + '\r', end='')
        
        print(message, end='', flush=True)
        self.last_length = len(message)
        
        # Nova linha no final
        if stats.current >= stats.total:
            print()
    
    def _format_message(self, stats: ProgressStats) -> str:
        """Formata mensagem de progresso"""
        progress_bar = ""
        
        if self.show_bar:
            filled = int(self.bar_width * stats.percentage / 100)
            bar = '█' * filled + '░' * (self.bar_width - filled)
            progress_bar = f"[{bar}] "
        
        return (f"\r{progress_bar}{stats.current:,}/{stats.total:,} "
                f"({stats.percentage:.1f}%) - "
                f"{stats.rate:.0f} itens/s - "
                f"ETA: {stats._format_time(stats.estimated_remaining_time)}")


class ChunkedProcessor:
    """Processador genérico com chunks e progresso"""
    
    def __init__(self, chunk_size: int = 500, 
                 progress_callback: Optional[Callable[[ProgressStats], None]] = None,
                 logger = None):
        self.chunk_size = chunk_size
        self.progress_callback = progress_callback or ConsoleProgressCallback()
        self.logger = logger
    
    def process(self, items: list, processor: Callable[[list], Dict[str, Any]], 
                description: str = "Processando") -> Dict[str, Any]:
        """
        Processa lista em chunks com progresso
        
        Args:
            items: Lista de itens para processar
            processor: Função que processa um chunk e retorna dict com estatísticas
            description: Descrição da operação
        """
        if not items:
            return {'processed': 0, 'errors': 0, 'time': 0}
        
        total_items = len(items)
        chunks = [items[i:i + self.chunk_size] for i in range(0, total_items, self.chunk_size)]
        
        if self.logger:
            self.logger.info(f"🔄 {description}: {total_items:,} itens em {len(chunks)} chunks")
        
        # Inicializa tracker
        tracker = ProgressTracker(
            total_items=total_items,
            chunk_size=self.chunk_size,
            callback=self.progress_callback
        )
        
        # Estatísticas agregadas
        total_processed = 0
        total_errors = 0
        total_duplicates = 0
        start_time = time.time()
        
        try:
            for chunk_idx, chunk in enumerate(chunks):
                chunk_start = time.time()
                
                # Processa chunk
                result = processor(chunk)
                
                # Extrai estatísticas do resultado
                chunk_processed = result.get('new', 0) + result.get('duplicates', 0)
                chunk_errors = result.get('errors', 0)
                chunk_duplicates = result.get('duplicates', 0)
                chunk_time = time.time() - chunk_start
                
                # Atualiza estatísticas totais
                total_processed += chunk_processed
                total_errors += chunk_errors
                total_duplicates += chunk_duplicates
                
                # Atualiza progresso
                extra_data = {
                    'chunk_idx': chunk_idx + 1,
                    'total_chunks': len(chunks),
                    'chunk_time': chunk_time,
                    'errors': total_errors,
                    'duplicates': total_duplicates
                }
                
                tracker.update(chunk_processed, extra_data)
                
                # Log detalhado se disponível
                if self.logger:
                    self.logger.debug(f"Chunk {chunk_idx + 1}/{len(chunks)}: "
                                    f"{chunk_processed} processados, "
                                    f"{chunk_errors} erros, "
                                    f"{chunk_time:.2f}s")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro durante processamento: {e}")
            raise
        
        finally:
            # Estatísticas finais
            total_time = time.time() - start_time
            
            if self.logger:
                rate = total_processed / total_time if total_time > 0 else 0
                self.logger.info(f"✅ {description} concluído: "
                               f"{total_processed:,} itens em {total_time:.2f}s "
                               f"({rate:.0f} itens/s)")
                
                if total_duplicates > 0:
                    self.logger.info(f"   • Duplicatas ignoradas: {total_duplicates:,}")
                if total_errors > 0:
                    self.logger.warning(f"   • Erros encontrados: {total_errors:,}")
        
        return {
            'processed': total_processed,
            'errors': total_errors,
            'duplicates': total_duplicates,
            'time': total_time,
            'rate': total_processed / total_time if total_time > 0 else 0
        }


# Callback customizado para diferentes tipos de dados
class TypedProgressCallback(ConsoleProgressCallback):
    """Callback que mostra tipo de dados sendo processados"""
    
    def __init__(self, data_type: str = "itens", **kwargs):
        super().__init__(**kwargs)
        self.data_type = data_type
    
    def _format_message(self, stats: ProgressStats) -> str:
        """Formata mensagem com tipo de dados"""
        progress_bar = ""
        
        if self.show_bar:
            filled = int(self.bar_width * stats.percentage / 100)
            bar = '█' * filled + '░' * (self.bar_width - filled)
            progress_bar = f"[{bar}] "
        
        # Adiciona informações extras se disponíveis
        extra_info = ""
        if hasattr(stats, 'duplicates') and stats.duplicates > 0:
            extra_info += f" (duplicatas: {stats.duplicates:,})"
        if hasattr(stats, 'errors') and stats.errors > 0:
            extra_info += f" (erros: {stats.errors:,})"
        
        return (f"\r{progress_bar}{stats.current:,}/{stats.total:,} {self.data_type} "
                f"({stats.percentage:.1f}%) - "
                f"{stats.rate:.0f}/s - "
                f"ETA: {stats._format_time(stats.estimated_remaining_time)}"
                f"{extra_info}")


if __name__ == "__main__":
    # Teste do sistema de progresso
    import random
    
    def simulate_processing(chunk):
        """Simula processamento de chunk"""
        time.sleep(0.1)  # Simula trabalho
        return {
            'new': len(chunk) - random.randint(0, 2),
            'duplicates': random.randint(0, 2),
            'errors': 0
        }
    
    # Teste
    items = list(range(1000))
    processor = ChunkedProcessor(
        chunk_size=50,
        progress_callback=TypedProgressCallback("produtos", show_bar=True)
    )
    
    result = processor.process(items, simulate_processing, "Teste de progresso")
    print(f"\nResultado: {result}")