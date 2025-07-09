#!/usr/bin/env python3
"""
Restaurant Element Finder - Element discovery and validation for restaurant scraping
"""

from typing import List, Dict, Any, Optional
from .selectors import RestaurantSelectors


class RestaurantElementFinder:
    """Element discovery and validation for restaurant scraping"""
    
    def __init__(self, logger):
        self.logger = logger
        self.selectors = RestaurantSelectors()
    
    def find_restaurant_elements(self, page) -> List[Any]:
        """
        Busca todos os elementos de restaurantes usando múltiplos seletores
        
        Args:
            page: Playwright page object
            
        Returns:
            List of restaurant elements found and validated
        """
        restaurant_elements = []
        successful_selector = None
        
        self.logger.info("Buscando restaurantes com diferentes seletores...")
        
        for selector in self.selectors.get_restaurant_selectors():
            try:
                elements = page.locator(selector).all()
                
                # Filtra elementos que realmente parecem ser restaurantes
                valid_elements = []
                for element in elements:
                    if self.validate_restaurant_element(element):
                        valid_elements.append(element)
                
                # Sempre pega o seletor que retorna mais elementos válidos
                if len(valid_elements) > len(restaurant_elements):
                    restaurant_elements = valid_elements
                    successful_selector = selector
                    self.logger.info(f"Seletor '{selector}': {len(valid_elements)} restaurantes válidos encontrados")
                
            except Exception as e:
                self.logger.debug(f"Seletor '{selector}' falhou: {str(e)}")
                continue
        
        if len(restaurant_elements) == 0:
            self.logger.warning("AVISO: Nenhum restaurante encontrado com nenhum seletor!")
            # Como último recurso, tenta capturar qualquer elemento que contenha informações de restaurante
            try:
                fallback_elements = page.locator('*').filter(has_text='R$').all()
                restaurant_elements = fallback_elements[:20]  # Limita a 20 para não sobrecarregar
                self.logger.info(f"Fallback: {len(restaurant_elements)} elementos com 'R$' encontrados")
            except:
                pass
        else:
            self.logger.info(f"SUCESSO: {len(restaurant_elements)} restaurantes encontrados usando '{successful_selector}'")
        
        return restaurant_elements
    
    def validate_restaurant_element(self, element) -> bool:
        """
        Valida se um elemento realmente parece ser um restaurante
        
        Args:
            element: Playwright element to validate
            
        Returns:
            True if element appears to be a restaurant, False otherwise
        """
        try:
            # Verifica se o elemento tem conteúdo de texto relevante
            text_content = element.inner_text().strip()
            
            # Critérios mais flexíveis para validação
            is_valid = False
            
            # Critério 1: Tem informações típicas de restaurante
            if (len(text_content) > 10 and 
                ('R$' in text_content or 'min' in text_content or 
                 any(word in text_content.lower() for word in ['delivery', 'entrega', 'rating', 'avaliação', 'estrela']))):
                is_valid = True
            
            # Critério 2: Tem link de restaurante ou imagem
            try:
                has_restaurant_link = element.locator('a[href*="/delivery/"], a[href*="/store/"], a[href*="/restaurant/"]').count() > 0
                has_image = element.locator('img').count() > 0
                if has_restaurant_link or (has_image and len(text_content) > 5):
                    is_valid = True
            except:
                pass
            
            # Critério 3: Estrutura típica de card de restaurante
            try:
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if len(lines) >= 2:
                    # Primeiro item pode ser nome, segundo pode ser categoria ou avaliação
                    first_line = lines[0]
                    if len(first_line) > 3 and not first_line.replace('.', '').replace(',', '').isdigit():
                        is_valid = True
            except:
                pass
            
            # Critério 4: Elemento com atributos específicos
            try:
                element_html = element.get_attribute('outerHTML') or ""
                if any(attr in element_html.lower() for attr in [
                    'restaurant', 'store', 'data-testid', 'delivery'
                ]):
                    is_valid = True
            except:
                pass
            
            return is_valid
            
        except Exception as e:
            self.logger.debug(f"Erro ao validar elemento: {e}")
            return False
    
    def count_restaurants_on_page(self, page) -> int:
        """
        Conta quantos restaurantes estão visíveis na página usando a mesma lógica de validação
        
        Args:
            page: Playwright page object
            
        Returns:
            Number of valid restaurant elements found
        """
        try:
            max_count = 0
            
            # Usa a mesma lógica de validação do extractor principal
            for selector in self.selectors.get_primary_selectors():  # Apenas os primeiros 5 para performance
                try:
                    elements = page.locator(selector).all()
                    valid_count = 0
                    
                    for element in elements[:100]:  # Limita para performance
                        if self._validate_element_quick(element):
                            valid_count += 1
                    
                    max_count = max(max_count, valid_count)
                    
                except:
                    continue
            
            # Se não encontrou nada com os seletores principais, usa fallback
            if max_count == 0:
                max_count = self._count_fallback_elements(page)
            
            return min(max_count, 500)  # Limite razoável
            
        except:
            return 0
    
    def _validate_element_quick(self, element) -> bool:
        """Validação rápida para contagem de elementos"""
        try:
            text_content = element.inner_text().strip()
            
            # Usa critérios simplificados para contagem rápida
            is_valid = False
            
            # Critério rápido: tem informações de restaurante
            if (len(text_content) > 10 and 
                ('R$' in text_content or 'min' in text_content)):
                is_valid = True
            
            # Critério rápido: tem link ou imagem
            elif element.locator('img').count() > 0 and len(text_content) > 5:
                is_valid = True
            
            return is_valid
            
        except:
            return False
    
    def _count_fallback_elements(self, page) -> int:
        """Conta elementos usando estratégia de fallback"""
        try:
            count = 0
            # Fallback: conta elementos que contêm R$ e parecem ter estrutura de restaurante
            fallback_elements = page.locator('*').filter(has_text='R$').all()
            for element in fallback_elements[:50]:  # Limita para performance
                try:
                    text = element.inner_text().strip()
                    lines = text.split('\n')
                    if len(lines) >= 2 and len(text) > 15:
                        count += 1
                except:
                    continue
            return count
        except:
            return 0