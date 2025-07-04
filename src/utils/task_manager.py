from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from queue import PriorityQueue
import uuid
import json


@dataclass
class Task:
    """Representa uma tarefa genérica"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    priority: int = 5  # 1 = alta, 10 = baixa
    data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """Para ordenação por prioridade na PriorityQueue"""
        return self.priority < other.priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte task para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority,
            'data': self.data,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'retries': self.retries
        }


class TaskManager:
    """Gerenciador de tarefas com fila de prioridade"""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.tasks = {}  # id -> Task
        self.completed_tasks = []
        self.failed_tasks = []
        
    def add_task(self, name: str, data: Dict[str, Any], priority: int = 5) -> Task:
        """Adiciona uma nova tarefa"""
        task = Task(name=name, data=data, priority=priority)
        self.queue.put((priority, task.id))
        self.tasks[task.id] = task
        return task
    
    def get_next_task(self) -> Optional[Task]:
        """Retorna a próxima tarefa da fila"""
        if self.queue.empty():
            return None
            
        _, task_id = self.queue.get()
        task = self.tasks.get(task_id)
        
        if task and task.status == "pending":
            task.status = "running"
            task.started_at = datetime.now()
            return task
            
        return self.get_next_task()  # Recursão para pegar próxima válida
    
    def complete_task(self, task_id: str, result: Any = None):
        """Marca tarefa como concluída"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            self.completed_tasks.append(task)
    
    def fail_task(self, task_id: str, error: str):
        """Marca tarefa como falha"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "failed"
            task.completed_at = datetime.now()
            task.error = error
            
            # Retry logic
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = "pending"
                task.started_at = None
                task.completed_at = None
                # Re-adiciona à fila com prioridade aumentada
                self.queue.put((task.priority - 1, task.id))
            else:
                self.failed_tasks.append(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das tarefas"""
        return {
            'total': len(self.tasks),
            'pending': sum(1 for t in self.tasks.values() if t.status == "pending"),
            'running': sum(1 for t in self.tasks.values() if t.status == "running"),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'queue_size': self.queue.qsize()
        }
    
    def save_results(self, filename: str):
        """Salva resultados em arquivo JSON"""
        results = {
            'stats': self.get_stats(),
            'completed': [t.to_dict() for t in self.completed_tasks],
            'failed': [t.to_dict() for t in self.failed_tasks],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


class BatchProcessor:
    """Processador de tarefas em lote"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.task_manager = TaskManager()
        
    def add_batch(self, items: List[Dict[str, Any]], task_name: str = "process", priority: int = 5):
        """Adiciona um lote de itens como tarefas"""
        tasks = []
        for item in items:
            task = self.task_manager.add_task(task_name, item, priority)
            tasks.append(task)
        return tasks
    
    def process_batch(self, processor_func: Callable[[Task], Any]):
        """Processa tarefas em lotes"""
        batch = []
        
        while True:
            task = self.task_manager.get_next_task()
            if not task:
                break
                
            batch.append(task)
            
            if len(batch) >= self.batch_size:
                # Processa o lote
                for task in batch:
                    try:
                        result = processor_func(task)
                        self.task_manager.complete_task(task.id, result)
                    except Exception as e:
                        self.task_manager.fail_task(task.id, str(e))
                
                batch = []
        
        # Processa tarefas restantes
        for task in batch:
            try:
                result = processor_func(task)
                self.task_manager.complete_task(task.id, result)
            except Exception as e:
                self.task_manager.fail_task(task.id, str(e))