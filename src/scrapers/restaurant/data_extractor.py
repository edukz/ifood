#!/usr/bin/env python3
"""
Restaurant Data Extractor - Data extraction and parsing for restaurant scraping
"""

import re
from typing import Dict, List, Any, Optional
from .selectors import RestaurantSelectors


class RestaurantDataExtractor:
    """Data extraction and parsing for restaurant scraping"""
    
    def __init__(self, logger, current_category: str = None):
        self.logger = logger
        self.current_category = current_category
        self.selectors = RestaurantSelectors()
    
    def extract_restaurant_data(self, element, index: int, total: int) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um elemento de restaurante específico
        
        Args:
            element: Playwright element containing restaurant data
            index: Current element index
            total: Total number of elements
            
        Returns:
            Dictionary with extracted restaurant data or None if invalid
        """
        try:
            restaurant_data = {}
            
            # Pega todo o texto do elemento para análise
            full_text = element.inner_text().strip()
            
            # Parse completo do texto estruturado
            parsed_data = self.parse_restaurant_text(full_text)
            
            if not parsed_data or not parsed_data.get('nome'):
                self.logger.debug(f"[{index}/{total}] Elemento ignorado: dados incompletos")
                return None
            
            # Usa dados parseados estruturados
            restaurant_data['nome'] = parsed_data['nome']
            restaurant_data['avaliacao'] = parsed_data.get('rating', 0.0)
            restaurant_data['categoria'] = parsed_data.get('categoria', self.current_category or "Não informado")
            restaurant_data['distancia'] = parsed_data.get('distancia', "Não informado")
            
            # Extrai URL do restaurante
            url = self.extract_restaurant_url(element)
            restaurant_data['url'] = url
            
            # Tempo de entrega - busca padrões específicos no texto
            tempo_entrega = self.extract_delivery_time(full_text)
            restaurant_data['tempo_entrega'] = tempo_entrega
            
            # Taxa de entrega - busca padrões específicos no texto  
            taxa_entrega = self.extract_delivery_fee(full_text)
            restaurant_data['taxa_entrega'] = taxa_entrega
            
            # Endereço/localização (se disponível)
            endereco = self.extract_text_safe(element, self.selectors.get_address_selectors())
            restaurant_data['endereco'] = endereco
            
            return restaurant_data
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados do restaurante {index}: {str(e)}")
            return None
    
    def extract_text_safe(self, element, selectors: List[str]) -> Optional[str]:
        """
        Tenta extrair texto usando múltiplos seletores
        
        Args:
            element: Playwright element to search within
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted text or None if not found
        """
        for selector in selectors:
            try:
                sub_element = element.locator(selector).first
                if sub_element.count() > 0:
                    text = sub_element.inner_text().strip()
                    if text:
                        return text
            except:
                continue
        return None
    
    def parse_restaurant_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Faz parse estruturado do texto do restaurante
        
        Args:
            text: Raw text content from restaurant element
            
        Returns:
            Dictionary with parsed restaurant data or None if invalid
        """
        try:
            if not text:
                return None
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) < 2:
                return None
            
            parsed = {}
            
            # Padrão esperado: NOME, RATING, •, CATEGORIA, •, DISTÂNCIA
            # Mas pode variar, então vamos ser flexível
            
            # Primeira linha sempre é o nome
            parsed['nome'] = lines[0]
            
            # Procura rating (número decimal entre 0-5)
            rating = 0.0
            for line in lines[1:]:
                try:
                    if line != '•' and '.' in line and len(line) <= 4:
                        rating_candidate = float(line.replace(',', '.'))
                        if 0 <= rating_candidate <= 5:
                            parsed['rating'] = rating_candidate
                            break
                except:
                    continue
            
            # Procura categoria (linha após rating, ignorando •)
            categoria = None
            for i, line in enumerate(lines):
                if line != '•' and not any(char in line for char in ['.', 'km', 'min', 'R$']):
                    # Se não é o nome e não contém números/símbolos, pode ser categoria
                    if line != parsed['nome']:
                        categoria = line
                        break
            parsed['categoria'] = categoria
            
            # Procura distância (contém 'km')
            distancia = None
            for line in lines:
                if 'km' in line.lower():
                    distancia = line
                    break
            parsed['distancia'] = distancia
            
            return parsed
            
        except Exception as e:
            self.logger.debug(f"Erro no parse do texto: {e}")
            return None
    
    def extract_delivery_time(self, text: str) -> str:
        """
        Extrai tempo de entrega do texto usando regex
        
        Args:
            text: Text content to search
            
        Returns:
            Extracted delivery time or "Não informado"
        """
        try:
            # Busca padrões como "30-40 min", "45 min", "1h 20min"
            time_patterns = [
                r'(\d+-\d+\s*min)',
                r'(\d+\s*min)',
                r'(\d+h\s*\d*min?)',
            ]
            for pattern in time_patterns:
                time_match = re.search(pattern, text, re.IGNORECASE)
                if time_match:
                    return time_match.group(1)
            return "Não informado"
        except Exception as e:
            self.logger.debug(f"Erro na extração do tempo de entrega: {e}")
            return "Não informado"
    
    def extract_delivery_fee(self, text: str) -> str:
        """
        Extrai taxa de entrega do texto usando regex
        
        Args:
            text: Text content to search
            
        Returns:
            Extracted delivery fee or "Não informado"
        """
        try:
            # Busca padrões de preço ou "grátis"
            fee_patterns = [
                r'(Grátis|grátis|GRÁTIS)',
                r'(R\$\s*\d+[.,]\d+)',
                r'(R\$\s*\d+)',
            ]
            for pattern in fee_patterns:
                fee_match = re.search(pattern, text)
                if fee_match:
                    return fee_match.group(1)
            return "Não informado"
        except Exception as e:
            self.logger.debug(f"Erro na extração da taxa de entrega: {e}")
            return "Não informado"
    
    def extract_restaurant_url(self, element) -> Optional[str]:
        """
        Extrai URL do restaurante do elemento
        
        Args:
            element: Playwright element containing restaurant data
            
        Returns:
            Restaurant URL or None if not found
        """
        try:
            # Tenta encontrar links diretos no elemento ou seus filhos
            for selector in self.selectors.get_url_selectors():
                try:
                    link_element = element.locator(selector).first
                    if link_element.count() > 0:
                        href = link_element.get_attribute('href')
                        if href:
                            # Se é uma URL relativa, adiciona o domínio base
                            if href.startswith('/'):
                                href = f"https://www.ifood.com.br{href}"
                            return href
                except:
                    continue
            
            # Tenta buscar por data-href ou outros atributos
            try:
                data_href = element.get_attribute('data-href')
                if data_href:
                    if data_href.startswith('/'):
                        return f"https://www.ifood.com.br{data_href}"
                    return data_href
            except:
                pass
            
            # Como último recurso, tenta encontrar o href no próprio elemento
            try:
                href = element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        return f"https://www.ifood.com.br{href}"
                    return href
            except:
                pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair URL do restaurante: {str(e)}")
            return None
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida se os dados extraídos são consistentes
        
        Args:
            data: Dictionary with extracted restaurant data
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Verifica se tem nome
            if not data.get('nome') or len(data['nome']) < 3:
                return False
            
            # Verifica se avaliação é válida
            rating = data.get('avaliacao', 0)
            if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
                return False
            
            # Verifica se tem pelo menos alguns dados básicos
            required_fields = ['nome', 'categoria', 'url']
            if not all(data.get(field) for field in required_fields):
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erro na validação dos dados: {e}")
            return False
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do extrator"""
        return {
            'patterns_supported': {
                'delivery_time': ['30-40 min', '45 min', '1h 20min'],
                'delivery_fee': ['Grátis', 'R$ 5,99', 'R$ 10'],
                'rating': ['4.5', '3.2', '5.0'],
                'distance': ['2.5 km', '1.8 km']
            },
            'selectors_count': {
                'restaurant': len(self.selectors.get_restaurant_selectors()),
                'url': len(self.selectors.get_url_selectors()),
                'address': len(self.selectors.get_address_selectors())
            }
        }