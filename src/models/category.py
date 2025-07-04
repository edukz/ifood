from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Category:
    """Modelo de dados para categoria de comida"""
    name: str
    url: str
    icon_url: Optional[str] = None
    slug: Optional[str] = None
    extracted_at: datetime = None
    
    def __post_init__(self):
        if not self.extracted_at:
            self.extracted_at = datetime.now()
        
        # Extrai slug da URL se não fornecido
        if not self.slug and self.url:
            # Exemplo: /delivery/cidade/categoria -> categoria
            parts = self.url.rstrip('/').split('/')
            if parts:
                self.slug = parts[-1]
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'name': self.name,
            'url': self.url,
            'icon_url': self.icon_url,
            'slug': self.slug,
            'extracted_at': self.extracted_at.isoformat()
        }