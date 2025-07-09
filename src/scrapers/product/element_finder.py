#!/usr/bin/env python3
"""
Product Element Finder - Element discovery and validation for product scraping
"""

from typing import List, Dict, Any, Optional
from .selectors import ProductSelectors


class ProductElementFinder:
    """Element discovery and validation for product scraping"""
    
    def __init__(self, logger):
        self.logger = logger
        self.selectors = ProductSelectors()
    
    def find_product_elements(self, page) -> List[Any]:
        """
        Busca elementos de produtos usando estratégia melhorada
        
        Args:
            page: Playwright page object
            
        Returns:
            List of product elements found and validated
        """
        
        # Seletores específicos para produtos do iFood (mais precisos)
        priority_selectors = [
            self.selectors.product_item_xpath,  # XPath original
            'li[data-testid="dish-card"]',  # Cards de pratos específicos
            'div[data-testid="menu-item"]',  # Items de menu
            'article[data-testid="product"]',  # Produtos
            'div[class*="dish-card"]',  # Cards de pratos por classe
            'li[class*="product"]',  # Products por classe
            'div[class*="menu-item"]',  # Items de menu por classe
        ]
        
        # Tenta cada seletor e retorna o que encontrar mais elementos válidos
        best_result = []
        best_selector = None
        best_count = 0
        
        for selector in priority_selectors:
            try:
                elements = page.locator(selector).all()
                if len(elements) > best_count:
                    # Valida se os elementos parecem ser produtos reais
                    valid_elements = self.validate_product_elements(elements[:50])  # Limita para validação
                    if len(valid_elements) > best_count:
                        best_result = elements  # Mantém todos os elementos, não só os validados
                        best_selector = selector
                        best_count = len(elements)
                        self.logger.info(f"Melhor seletor até agora: {selector} ({len(elements)} elementos, {len(valid_elements)} válidos)")
            except Exception as e:
                self.logger.debug(f"Erro testando seletor {selector}: {str(e)}")
                continue
        
        if best_result:
            self.logger.info(f"SELETOR FINAL: {best_selector} com {len(best_result)} produtos")
            return best_result
        
        # Fallback: busca por elementos com preço
        self.logger.warning("Nenhum seletor específico funcionou, tentando fallback por preço...")
        try:
            elements = page.locator('*:has-text("R$")').all()
            valid_elements = self.validate_product_elements(elements[:100])
            
            if valid_elements:
                self.logger.info(f"Encontrados {len(valid_elements)} produtos via busca por preço")
                return valid_elements
                
        except Exception as e:
            self.logger.error(f"Erro no fallback por preço: {str(e)}")
        
        self.logger.error("ERRO: Nenhum produto encontrado com nenhum seletor!")
        return []
    
    def validate_product_elements(self, elements) -> List[Any]:
        """
        Valida se elementos parecem ser produtos reais
        
        Args:
            elements: List of Playwright elements to validate
            
        Returns:
            List of valid product elements
        """
        valid_elements = []
        
        for elem in elements:
            try:
                text = elem.inner_text().strip()
                
                # Critérios de validação para produtos
                if (len(text) > 5 and  # Tem texto mínimo
                    len(text) < 1000 and  # Não é texto muito longo
                    ('R$' in text or  # Tem preço OU
                     any(word in text.lower() for word in ['açaí', 'combo', 'ml', 'kg', 'g', 'unid'])  # Tem palavras de produto
                    )):
                    valid_elements.append(elem)
                    
            except Exception as e:
                self.logger.debug(f"Erro validando elemento: {str(e)}")
                continue
                
        return valid_elements
    
    def count_products_on_page(self, page) -> int:
        """
        Conta produtos visíveis na página usando a mesma lógica de validação
        
        Args:
            page: Playwright page object
            
        Returns:
            Number of valid product elements found
        """
        try:
            # Usa seletores primários para contagem rápida
            max_count = 0
            
            for selector in self.selectors.get_primary_selectors():
                try:
                    elements = page.locator(selector).all()
                    if len(elements) > max_count:
                        # Validação rápida
                        valid_count = self._count_valid_elements_quick(elements[:50])
                        if valid_count > max_count:
                            max_count = len(elements)  # Usa total, não apenas validados
                except:
                    continue
            
            return max_count
            
        except Exception as e:
            self.logger.debug(f"Erro ao contar produtos: {e}")
            return 0
    
    def _count_valid_elements_quick(self, elements) -> int:
        """
        Contagem rápida de elementos válidos para performance
        
        Args:
            elements: List of elements to count
            
        Returns:
            Number of valid elements
        """
        valid_count = 0
        
        for elem in elements:
            try:
                text = elem.inner_text().strip()
                
                # Critérios simplificados para contagem rápida
                if (len(text) > 5 and 
                    len(text) < 1000 and 
                    'R$' in text):
                    valid_count += 1
                    
            except:
                continue
                
        return valid_count
    
    def find_products_by_container(self, page) -> List[Any]:
        """
        Busca produtos através de containers específicos
        
        Args:
            page: Playwright page object
            
        Returns:
            List of product elements found in containers
        """
        products = []
        
        for container_selector in self.selectors.get_container_selectors():
            try:
                container = page.locator(container_selector).first
                if container.count() > 0:
                    # Busca produtos dentro do container
                    for product_selector in self.selectors.get_primary_selectors():
                        try:
                            elements = container.locator(product_selector).all()
                            if elements:
                                valid_elements = self.validate_product_elements(elements)
                                if valid_elements:
                                    products.extend(valid_elements)
                                    self.logger.info(f"Encontrados {len(valid_elements)} produtos em {container_selector}")
                                    break
                        except:
                            continue
                    
                    if products:
                        break
                        
            except Exception as e:
                self.logger.debug(f"Erro ao buscar em container {container_selector}: {e}")
                continue
        
        return products
    
    def find_products_by_xpath(self, page) -> List[Any]:
        """
        Busca produtos usando XPath específico
        
        Args:
            page: Playwright page object
            
        Returns:
            List of product elements found via XPath
        """
        try:
            elements = page.locator(self.selectors.product_item_xpath).all()
            if elements:
                valid_elements = self.validate_product_elements(elements)
                self.logger.info(f"XPath encontrou {len(elements)} elementos, {len(valid_elements)} válidos")
                return elements  # Retorna todos, não apenas válidos
            
        except Exception as e:
            self.logger.debug(f"Erro na busca por XPath: {e}")
        
        return []
    
    def find_products_with_price(self, page) -> List[Any]:
        """
        Busca produtos que contêm preço (fallback strategy)
        
        Args:
            page: Playwright page object
            
        Returns:
            List of product elements that contain price information
        """
        try:
            # Busca por elementos que contêm R$
            elements = page.locator('*:has-text("R$")').all()
            valid_elements = self.validate_product_elements(elements[:100])
            
            if valid_elements:
                self.logger.info(f"Busca por preço encontrou {len(valid_elements)} produtos válidos")
                return valid_elements
                
        except Exception as e:
            self.logger.error(f"Erro na busca por preço: {e}")
        
        return []
    
    def get_element_statistics(self, elements) -> Dict[str, Any]:
        """
        Analisa estatísticas dos elementos encontrados
        
        Args:
            elements: List of elements to analyze
            
        Returns:
            Dictionary with element statistics
        """
        stats = {
            'total_elements': len(elements),
            'valid_elements': 0,
            'elements_with_price': 0,
            'elements_with_images': 0,
            'average_text_length': 0,
            'validation_errors': 0
        }
        
        total_text_length = 0
        
        for elem in elements:
            try:
                text = elem.inner_text().strip()
                total_text_length += len(text)
                
                # Verifica se é válido
                if (len(text) > 5 and len(text) < 1000 and 
                    ('R$' in text or any(word in text.lower() for word in ['açaí', 'combo', 'ml', 'kg', 'g', 'unid']))):
                    stats['valid_elements'] += 1
                
                # Verifica se tem preço
                if 'R$' in text:
                    stats['elements_with_price'] += 1
                
                # Verifica se tem imagem
                try:
                    if elem.locator('img').count() > 0:
                        stats['elements_with_images'] += 1
                except:
                    pass
                    
            except Exception as e:
                stats['validation_errors'] += 1
                continue
        
        if stats['total_elements'] > 0:
            stats['average_text_length'] = total_text_length / stats['total_elements']
            stats['validity_rate'] = (stats['valid_elements'] / stats['total_elements']) * 100
            stats['price_rate'] = (stats['elements_with_price'] / stats['total_elements']) * 100
            stats['image_rate'] = (stats['elements_with_images'] / stats['total_elements']) * 100
        
        return stats
    
    def get_finder_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do finder"""
        return {
            'priority_selectors': [
                'XPath original',
                'dish-card testid',
                'menu-item testid',
                'product testid',
                'dish-card class',
                'product class',
                'menu-item class'
            ],
            'validation_criteria': [
                'text length > 5',
                'text length < 1000',
                'contains R$ OR product keywords',
                'product keywords: açaí, combo, ml, kg, g, unid'
            ],
            'fallback_strategies': [
                'search by price (R$)',
                'search by containers',
                'search by XPath only'
            ],
            'performance_limits': {
                'validation_batch_size': 50,
                'price_search_limit': 100,
                'primary_selectors_count': 5
            }
        }