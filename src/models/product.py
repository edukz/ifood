from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Product:
    """Modelo de dados para produto/item do cardápio"""
    nome: str
    descricao: Optional[str] = None
    preco: str = "Não informado"
    preco_original: Optional[str] = None  # Para quando há desconto
    categoria_produto: str = "Não informado"
    disponivel: bool = True
    imagem_url: Optional[str] = None
    tempo_preparo: Optional[str] = None
    serve_pessoas: Optional[int] = None
    calorias: Optional[str] = None
    tags: Optional[List[str]] = None
    ingredientes: Optional[List[str]] = None
    observacoes: Optional[str] = None
    restaurant_id: Optional[str] = None
    restaurant_name: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'preco_original': self.preco_original,
            'categoria_produto': self.categoria_produto,
            'disponivel': self.disponivel,
            'imagem_url': self.imagem_url,
            'tempo_preparo': self.tempo_preparo,
            'serve_pessoas': self.serve_pessoas,
            'calorias': self.calorias,
            'tags': ', '.join(self.tags) if self.tags else None,
            'ingredientes': ', '.join(self.ingredientes) if self.ingredientes else None,
            'observacoes': self.observacoes,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant_name,
            'extracted_at': self.extracted_at.isoformat()
        }