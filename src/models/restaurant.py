from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Restaurant:
    """Modelo de dados para restaurante"""
    nome: str
    categoria: str
    avaliacao: float = 0.0
    tempo_entrega: str = "Não informado"
    taxa_entrega: str = "Não informado"
    distancia: str = "Não informado"
    url: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    horario_funcionamento: Optional[str] = None
    pedido_minimo: Optional[str] = None
    promocoes: Optional[List[str]] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'nome': self.nome,
            'categoria': self.categoria,
            'avaliacao': self.avaliacao,
            'tempo_entrega': self.tempo_entrega,
            'taxa_entrega': self.taxa_entrega,
            'distancia': self.distancia,
            'url': self.url,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'horario_funcionamento': self.horario_funcionamento,
            'pedido_minimo': self.pedido_minimo,
            'promocoes': ', '.join(self.promocoes) if self.promocoes else None,
            'extracted_at': self.extracted_at.isoformat()
        }