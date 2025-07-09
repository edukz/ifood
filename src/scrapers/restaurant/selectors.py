#!/usr/bin/env python3
"""
Restaurant Selectors - Centralized selector management for restaurant scraping
"""

from typing import List


class RestaurantSelectors:
    """Centralized selector management for restaurant elements"""
    
    # Seletores otimizados para capturar mais restaurantes
    restaurant_selectors: List[str] = [
        # Seletores específicos do iFood
        'div[data-testid="restaurant-card"]',
        'article[data-testid="restaurant"]',
        'li[data-testid="restaurant"]',
        'div[data-testid="store-card"]',
        '[data-testid*="restaurant"]',
        '[data-testid*="store"]',
        
        # Seletores por links
        'a[href*="/delivery/"]',
        'a[href*="/store/"]', 
        'a[href*="/restaurant/"]',
        
        # Seletores por classes
        'div[class*="restaurant-card"]',
        'div[class*="store-card"]',
        'article[class*="restaurant"]',
        'article[class*="store"]',
        '[class*="restaurant-item"]',
        '[class*="store-item"]',
        
        # Seletores por estrutura
        'div[role="listitem"]',
        'li[role="listitem"]',
        
        # Seletores mais amplos (ordenados por especificidade)
        'article:has(img)',  # Artigos com imagens
        'div:has(a[href*="delivery"]):has(img)',  # Divs com links de delivery e imagens
        'li:has(img):has-text("R$")',  # Items de lista com imagem e preço
        'div:has-text("R$"):has(img)',  # Divs com preço e imagem
        
        # Fallbacks mais genéricos
        'article',
        'li'
    ]
    
    # Seletores para botões "Ver mais" ou similares
    load_more_selectors: List[str] = [
        'button:has-text("Ver mais")',
        'button:has-text("Carregar mais")', 
        'button:has-text("Mostrar mais")',
        'button:has-text("Mais restaurantes")',
        'button:has-text("Carregando...")',
        '[data-testid="load-more"]',
        '[data-testid="show-more"]',
        '.load-more-button',
        '.show-more',
        '.pagination-next',
        'button[class*="load"]',
        'button[class*="more"]',
        'a:has-text("Próxima")',
        'a:has-text(">")',
        # Seletores específicos do iFood
        '[data-testid="restaurant-list-pagination"]',
        '[class*="pagination"]',
        '[class*="load-more"]'
    ]
    
    # Seletores para URL do restaurante
    url_selectors: List[str] = [
        'a[href*="/delivery/"]',  # Links que contêm delivery
        'a[href*="/restaurant/"]',  # Links que contêm restaurant
        'a[href*="/store/"]',  # Links que contêm store
        'a[href]',  # Qualquer link
        '[data-href]',  # Elementos com data-href
        '[onclick*="href"]'  # Elementos com onclick que contém href
    ]
    
    # Seletores para campos específicos
    address_selectors: List[str] = [
        '[data-testid="address"]',
        'span[class*="address"]',
        'div[class*="location"]'
    ]
    
    @classmethod
    def get_restaurant_selectors(cls) -> List[str]:
        """Retorna lista de seletores para restaurantes"""
        return cls.restaurant_selectors.copy()
    
    @classmethod
    def get_load_more_selectors(cls) -> List[str]:
        """Retorna lista de seletores para botões 'Ver mais'"""
        return cls.load_more_selectors.copy()
    
    @classmethod
    def get_url_selectors(cls) -> List[str]:
        """Retorna lista de seletores para URLs"""
        return cls.url_selectors.copy()
    
    @classmethod
    def get_address_selectors(cls) -> List[str]:
        """Retorna lista de seletores para endereços"""
        return cls.address_selectors.copy()
    
    @classmethod
    def get_primary_selectors(cls, limit: int = 5) -> List[str]:
        """Retorna os seletores primários (mais específicos) para performance"""
        return cls.restaurant_selectors[:limit]
    
    @classmethod
    def get_fallback_selectors(cls) -> List[str]:
        """Retorna seletores de fallback para casos extremos"""
        return cls.restaurant_selectors[-2:]  # 'article', 'li'