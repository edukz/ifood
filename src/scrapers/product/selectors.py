#!/usr/bin/env python3
"""
Product Selectors - Centralized selector management for product scraping
"""

from typing import List, Dict, Any


class ProductSelectors:
    """Centralized selector management for product elements"""
    
    # XPath base fornecido (mais específico)
    products_list_xpath = '//*[@id="__next"]/div[1]/main/div[1]/div/div[2]/div/div[5]/ul'
    product_item_xpath = f'{products_list_xpath}/li'
    
    # Seletores mais específicos e abrangentes para produtos
    product_selectors: List[str] = [
        # Seletores baseados no XPath original
        'ul li',  # Items de lista simples
        '#__next li',  # Items dentro do container principal
        'main li',  # Items dentro do main
        
        # Seletores específicos do iFood
        'li[data-testid="dish-card"]',
        'div[data-testid="menu-item"]',
        'article[data-testid="product"]',
        'div[data-testid="dish"]',
        
        # Seletores por classe
        'div[class*="dish-card"]',
        'div[class*="menu-item"]',
        'div[class*="product-card"]',
        'li[class*="product"]',
        'div[class*="item-card"]',
        'article[class*="dish"]',
        
        # Seletores genéricos mas filtrados
        'li:has-text("R$")',  # Items que contêm preço
        'div:has-text("R$"):has-text("Adicionar")',  # Divs com preço e botão
        '*[role="listitem"]',  # Elementos com role de item de lista
    ]
    
    # Seletores para containers de produtos
    container_selectors: List[str] = [
        products_list_xpath,
        'ul[class*="menu"]',
        'div[class*="menu-container"]',
        'section[class*="products"]',
        'div[class*="dishes"]',
        'ul[role="list"]'
    ]
    
    # Seletores para preços
    price_selectors: List[str] = [
        'span[class*="price"]',
        'div[class*="price"]',
        'span[class*="value"]',
        'div[class*="amount"]',
        '[data-testid="price"]',
        '[data-testid="value"]'
    ]
    
    # Seletores para categorias
    category_selectors: List[str] = [
        'span[class*="category"]',
        'div[class*="category"]',
        'p[class*="category"]',
        '[data-testid="category"]',
        'h2',
        'h3'
    ]
    
    # Seletores para imagens
    image_selectors: List[str] = [
        'img[src*="dishes"]',
        'img[src*="products"]',
        'img[src*="menu"]',
        'img[alt*="dish"]',
        'img[alt*="product"]',
        'img[alt*="item"]',
        'img'
    ]
    
    # Seletores para tags/badges
    tag_selectors: List[str] = [
        'span[class*="tag"]',
        'span[class*="badge"]',
        'div[class*="label"]',
        'span[class*="promotion"]',
        'div[class*="offer"]',
        '[data-testid="tag"]',
        '[data-testid="badge"]'
    ]
    
    # Seletores para botões de adicionar
    add_button_selectors: List[str] = [
        'button:has-text("Adicionar")',
        'button[class*="add"]',
        'button[class*="cart"]',
        '[data-testid="add-button"]',
        '[data-testid="add-to-cart"]'
    ]
    
    # Seletores para indicadores de disponibilidade
    availability_selectors: List[str] = [
        '[data-testid="availability"]',
        'span[class*="available"]',
        'span[class*="unavailable"]',
        'div[class*="sold-out"]',
        'div[class*="disabled"]'
    ]
    
    @classmethod
    def get_product_selectors(cls) -> List[str]:
        """Retorna lista de seletores para produtos"""
        return cls.product_selectors.copy()
    
    @classmethod
    def get_container_selectors(cls) -> List[str]:
        """Retorna lista de seletores para containers"""
        return cls.container_selectors.copy()
    
    @classmethod
    def get_price_selectors(cls) -> List[str]:
        """Retorna lista de seletores para preços"""
        return cls.price_selectors.copy()
    
    @classmethod
    def get_category_selectors(cls) -> List[str]:
        """Retorna lista de seletores para categorias"""
        return cls.category_selectors.copy()
    
    @classmethod
    def get_image_selectors(cls) -> List[str]:
        """Retorna lista de seletores para imagens"""
        return cls.image_selectors.copy()
    
    @classmethod
    def get_tag_selectors(cls) -> List[str]:
        """Retorna lista de seletores para tags/badges"""
        return cls.tag_selectors.copy()
    
    @classmethod
    def get_add_button_selectors(cls) -> List[str]:
        """Retorna lista de seletores para botões de adicionar"""
        return cls.add_button_selectors.copy()
    
    @classmethod
    def get_availability_selectors(cls) -> List[str]:
        """Retorna lista de seletores para disponibilidade"""
        return cls.availability_selectors.copy()
    
    @classmethod
    def get_primary_selectors(cls, limit: int = 5) -> List[str]:
        """Retorna os seletores primários (mais específicos) para performance"""
        return cls.product_selectors[:limit]
    
    @classmethod
    def get_xpath_selectors(cls) -> Dict[str, str]:
        """Retorna seletores XPath específicos"""
        return {
            'products_list': cls.products_list_xpath,
            'product_item': cls.product_item_xpath
        }
    
    @classmethod
    def get_fallback_selectors(cls) -> List[str]:
        """Retorna seletores de fallback para casos extremos"""
        return [
            'li:has-text("R$")',
            'div:has-text("R$"):has-text("Adicionar")',
            '*[role="listitem"]'
        ]
    
    @classmethod
    def get_selector_statistics(cls) -> Dict[str, int]:
        """Retorna estatísticas dos seletores"""
        return {
            'product_selectors': len(cls.product_selectors),
            'container_selectors': len(cls.container_selectors),
            'price_selectors': len(cls.price_selectors),
            'category_selectors': len(cls.category_selectors),
            'image_selectors': len(cls.image_selectors),
            'tag_selectors': len(cls.tag_selectors),
            'add_button_selectors': len(cls.add_button_selectors),
            'availability_selectors': len(cls.availability_selectors),
            'total_selectors': (
                len(cls.product_selectors) +
                len(cls.container_selectors) +
                len(cls.price_selectors) +
                len(cls.category_selectors) +
                len(cls.image_selectors) +
                len(cls.tag_selectors) +
                len(cls.add_button_selectors) +
                len(cls.availability_selectors)
            )
        }