#!/usr/bin/env python3
"""
Product Data Extractor - Data extraction and parsing for product scraping
"""

import re
from typing import Dict, List, Any, Optional
from .selectors import ProductSelectors


class ProductDataExtractor:
    """Data extraction and parsing for product scraping"""
    
    def __init__(self, logger, current_restaurant: str = None, current_restaurant_id: str = None):
        self.logger = logger
        self.current_restaurant = current_restaurant
        self.current_restaurant_id = current_restaurant_id
        self.selectors = ProductSelectors()
    
    def extract_product_data(self, element, index: int, total: int) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um elemento de produto específico
        
        Args:
            element: Playwright element containing product data
            index: Current element index
            total: Total number of elements
            
        Returns:
            Dictionary with extracted product data or None if invalid
        """
        try:
            product_data = {
                'restaurant_id': self.current_restaurant_id,
                'restaurant_name': self.current_restaurant
            }
            
            # Pega todo o texto do elemento
            full_text = element.inner_text().strip()
            
            # Nome do produto (geralmente a primeira linha ou texto mais proeminente)
            lines = full_text.split('\n')
            product_data['nome'] = lines[0] if lines else "Produto sem nome"
            
            # Descrição (geralmente segunda linha ou texto mais longo)
            if len(lines) > 1:
                # Busca linha que parece ser descrição (não é preço nem tag)
                for line in lines[1:]:
                    if len(line) > 20 and 'R$' not in line and not line.isupper():
                        product_data['descricao'] = line
                        break
            
            # Preço
            price = self.extract_price(full_text)
            product_data['preco'] = price['current']
            product_data['preco_original'] = price['original']
            
            # Categoria do produto (se disponível no elemento)
            product_data['categoria_produto'] = self.extract_product_category(element)
            
            # Imagem
            product_data['imagem_url'] = self.extract_image_url(element)
            
            # Tags/badges (promoção, novo, etc)
            product_data['tags'] = self.extract_tags(full_text)
            
            # Disponibilidade
            product_data['disponivel'] = self.check_availability(element, full_text)
            
            # Informações adicionais
            additional_info = self.extract_additional_info(full_text)
            product_data.update(additional_info)
            
            return product_data
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados do produto {index}: {str(e)}")
            return None
    
    def extract_price(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai preço do texto usando regex
        
        Args:
            text: Text content to search for price
            
        Returns:
            Dictionary with current and original prices
        """
        try:
            # Padrões de preço
            price_pattern = r'R\$\s*(\d+[.,]\d{2})'
            prices = re.findall(price_pattern, text)
            
            if not prices:
                return {'current': 'Não informado', 'original': None}
            
            if len(prices) == 1:
                return {'current': f'R$ {prices[0]}', 'original': None}
            
            # Se há 2 preços, pode ser original e com desconto
            if len(prices) >= 2:
                # Assume que o maior é o original e o menor é o atual
                price_values = [float(p.replace(',', '.')) for p in prices]
                if price_values[0] > price_values[1]:
                    return {'current': f'R$ {prices[1]}', 'original': f'R$ {prices[0]}'}
                else:
                    return {'current': f'R$ {prices[0]}', 'original': f'R$ {prices[1]}'}
            
            return {'current': f'R$ {prices[0]}', 'original': None}
            
        except Exception as e:
            self.logger.debug(f"Erro na extração de preço: {e}")
            return {'current': 'Não informado', 'original': None}
    
    def extract_product_category(self, element) -> str:
        """
        Extrai categoria do produto se disponível
        
        Args:
            element: Playwright element containing product data
            
        Returns:
            Product category or "Não categorizado"
        """
        try:
            # Busca por elementos que indiquem categoria
            category_selectors = [
                '[data-testid="category-name"]',
                '[class*="category"]',
                '[class*="section"]'
            ]
            
            for selector in category_selectors:
                try:
                    cat_elem = element.locator(selector).first
                    if cat_elem.count() > 0:
                        return cat_elem.inner_text().strip()
                except:
                    continue
            
            return "Não categorizado"
            
        except Exception as e:
            self.logger.debug(f"Erro na extração de categoria: {e}")
            return "Não categorizado"
    
    def extract_image_url(self, element) -> Optional[str]:
        """
        Extrai URL da imagem do produto
        
        Args:
            element: Playwright element containing product data
            
        Returns:
            Image URL or None if not found
        """
        try:
            # Busca imagens no elemento
            img_element = element.locator('img').first
            if img_element.count() > 0:
                src = img_element.get_attribute('src')
                if src and src.startswith('http'):
                    return src
            
            # Tenta background-image
            style_elements = element.locator('[style*="background-image"]').all()
            for style_elem in style_elements:
                style = style_elem.get_attribute('style')
                if style and 'url(' in style:
                    url_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    if url_match:
                        return url_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erro na extração de imagem: {e}")
            return None
    
    def extract_tags(self, text: str) -> Optional[List[str]]:
        """
        Extrai tags/badges do produto
        
        Args:
            text: Text content to search for tags
            
        Returns:
            List of tags or None if no tags found
        """
        tags = []
        
        # Palavras que indicam tags
        tag_keywords = [
            'promoção', 'desconto', 'novo', 'mais pedido', 
            'destaque', 'especial', 'limitado', 'vegano',
            'vegetariano', 'sem glúten', 'fit', 'light',
            'picante', 'promocao', '%', 'off'
        ]
        
        text_lower = text.lower()
        for keyword in tag_keywords:
            if keyword in text_lower:
                tags.append(keyword.title())
        
        return tags if tags else None
    
    def check_availability(self, element, text: str) -> bool:
        """
        Verifica se o produto está disponível
        
        Args:
            element: Playwright element containing product data
            text: Text content to check
            
        Returns:
            True if product is available, False otherwise
        """
        try:
            unavailable_keywords = [
                'indisponível', 'esgotado', 'sold out', 
                'unavailable', 'fora de estoque'
            ]
            
            text_lower = text.lower()
            for keyword in unavailable_keywords:
                if keyword in text_lower:
                    return False
            
            # Verifica se o elemento está desabilitado
            try:
                if element.get_attribute('disabled'):
                    return False
            except:
                pass
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erro na verificação de disponibilidade: {e}")
            return True  # Assume disponível em caso de erro
    
    def extract_additional_info(self, text: str) -> Dict[str, Any]:
        """
        Extrai informações adicionais do produto
        
        Args:
            text: Text content to extract additional info from
            
        Returns:
            Dictionary with additional product information
        """
        info = {}
        
        try:
            # Serve quantas pessoas
            serves_match = re.search(r'serve[s]?\s*(\d+)\s*pessoa', text, re.IGNORECASE)
            if serves_match:
                info['serve_pessoas'] = int(serves_match.group(1))
            
            # Tempo de preparo
            time_match = re.search(r'(\d+[-\s]?\d*)\s*min', text, re.IGNORECASE)
            if time_match:
                info['tempo_preparo'] = time_match.group(0)
            
            # Calorias
            cal_match = re.search(r'(\d+)\s*kcal|calorias', text, re.IGNORECASE)
            if cal_match:
                info['calorias'] = cal_match.group(0)
            
            # Peso ou volume
            weight_match = re.search(r'(\d+)\s*(kg|g|ml|l)\b', text, re.IGNORECASE)
            if weight_match:
                info['peso_volume'] = weight_match.group(0)
            
            # Ingredientes (se mencionados)
            ingredients_patterns = [
                r'ingredientes?:\s*([^.]+)',
                r'contém:\s*([^.]+)',
                r'feito com:\s*([^.]+)'
            ]
            
            for pattern in ingredients_patterns:
                ingredients_match = re.search(pattern, text, re.IGNORECASE)
                if ingredients_match:
                    info['ingredientes'] = ingredients_match.group(1).strip()
                    break
            
        except Exception as e:
            self.logger.debug(f"Erro na extração de informações adicionais: {e}")
        
        return info
    
    def extract_nutritional_info(self, text: str) -> Dict[str, Any]:
        """
        Extrai informações nutricionais do produto
        
        Args:
            text: Text content to extract nutritional info from
            
        Returns:
            Dictionary with nutritional information
        """
        nutrition = {}
        
        try:
            # Padrões para informações nutricionais
            nutrition_patterns = {
                'proteinas': r'(\d+[.,]?\d*)\s*g?\s*de?\s*proteína',
                'carboidratos': r'(\d+[.,]?\d*)\s*g?\s*de?\s*carboidrato',
                'gorduras': r'(\d+[.,]?\d*)\s*g?\s*de?\s*gordura',
                'fibras': r'(\d+[.,]?\d*)\s*g?\s*de?\s*fibra',
                'sodio': r'(\d+[.,]?\d*)\s*mg?\s*de?\s*sódio'
            }
            
            for nutrient, pattern in nutrition_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nutrition[nutrient] = match.group(1)
            
        except Exception as e:
            self.logger.debug(f"Erro na extração de informações nutricionais: {e}")
        
        return nutrition
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida se os dados extraídos são consistentes
        
        Args:
            data: Dictionary with extracted product data
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Verifica se tem nome
            if not data.get('nome') or len(data['nome']) < 3:
                return False
            
            # Verifica se tem preço válido
            if data.get('preco') == 'Não informado':
                return False
            
            # Verifica se tem dados mínimos necessários
            required_fields = ['nome', 'preco', 'restaurant_name']
            if not all(data.get(field) for field in required_fields):
                return False
            
            # Verifica se não é um elemento que parece ser menu/categoria
            nome_lower = data['nome'].lower()
            invalid_names = ['menu', 'categoria', 'seção', 'cardápio', 'opções']
            if any(invalid in nome_lower for invalid in invalid_names):
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erro na validação dos dados: {e}")
            return False
    
    def get_price_statistics(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa estatísticas de preços dos produtos extraídos
        
        Args:
            products_data: List of product dictionaries
            
        Returns:
            Dictionary with price statistics
        """
        stats = {
            'total_products': len(products_data),
            'products_with_price': 0,
            'products_with_discount': 0,
            'average_price': 0,
            'min_price': float('inf'),
            'max_price': 0,
            'price_ranges': {
                'ate_10': 0,
                'de_10_25': 0,
                'de_25_50': 0,
                'acima_50': 0
            }
        }
        
        total_price = 0
        valid_prices = []
        
        for product in products_data:
            price_str = product.get('preco', 'Não informado')
            
            if price_str != 'Não informado':
                stats['products_with_price'] += 1
                
                # Extrai valor numérico do preço
                try:
                    price_match = re.search(r'R\$\s*(\d+[.,]\d{2})', price_str)
                    if price_match:
                        price_value = float(price_match.group(1).replace(',', '.'))
                        valid_prices.append(price_value)
                        total_price += price_value
                        
                        # Atualiza min/max
                        stats['min_price'] = min(stats['min_price'], price_value)
                        stats['max_price'] = max(stats['max_price'], price_value)
                        
                        # Categoriza por faixa de preço
                        if price_value <= 10:
                            stats['price_ranges']['ate_10'] += 1
                        elif price_value <= 25:
                            stats['price_ranges']['de_10_25'] += 1
                        elif price_value <= 50:
                            stats['price_ranges']['de_25_50'] += 1
                        else:
                            stats['price_ranges']['acima_50'] += 1
                            
                except:
                    pass
            
            # Verifica se tem desconto
            if product.get('preco_original'):
                stats['products_with_discount'] += 1
        
        # Calcula média
        if valid_prices:
            stats['average_price'] = total_price / len(valid_prices)
        else:
            stats['min_price'] = 0
        
        return stats
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do extrator"""
        return {
            'supported_fields': [
                'nome', 'descricao', 'preco', 'preco_original',
                'categoria_produto', 'imagem_url', 'tags',
                'disponivel', 'serve_pessoas', 'tempo_preparo',
                'calorias', 'peso_volume', 'ingredientes'
            ],
            'price_patterns': [
                'R$ XX,XX',
                'R$ X,XX',
                'Multiple prices (discount detection)'
            ],
            'tag_keywords': [
                'promoção', 'desconto', 'novo', 'mais pedido',
                'destaque', 'especial', 'limitado', 'vegano',
                'vegetariano', 'sem glúten', 'fit', 'light',
                'picante', 'promocao', '%', 'off'
            ],
            'validation_rules': [
                'nome length >= 3',
                'preco != "Não informado"',
                'required fields present',
                'not menu/category name'
            ],
            'additional_info_patterns': [
                'serve X pessoas',
                'X min (tempo preparo)',
                'X kcal (calorias)',
                'X kg/g/ml/l (peso/volume)',
                'ingredientes/contém/feito com'
            ]
        }