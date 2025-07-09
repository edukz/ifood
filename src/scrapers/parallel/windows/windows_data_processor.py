#!/usr/bin/env python3
"""
Windows Data Processor - Processamento e coordenação de dados para scraping paralelo
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.logger import setup_logger
from .windows_data_generator import WindowsDataGenerator
from .windows_database_manager import WindowsDatabaseManager


class WindowsDataProcessor:
    """Processador de dados para extração paralela no Windows"""
    
    def __init__(self):
        self.logger = setup_logger("WindowsDataProcessor")
        self.data_generator = WindowsDataGenerator()
        self.db_manager = WindowsDatabaseManager()
    
    async def extract_products_for_restaurant(self, restaurant_data: Dict[str, Any], 
                                            products_per_restaurant: int = 10) -> List[Dict[str, Any]]:
        """Extrai produtos para um restaurante específico"""
        products = []
        
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurante Desconhecido')
            category = restaurant_data.get('category', 'geral')
            restaurant_id = restaurant_data.get('id')
            
            if not restaurant_id:
                self.logger.warning(f"ID do restaurante não encontrado para {restaurant_name}")
                return products
            
            # Obter produtos da categoria
            category_products = self._get_category_products(category)
            
            # Gerar produtos para o restaurante
            for i in range(products_per_restaurant):
                try:
                    # Selecionar produto base
                    if i < len(category_products):
                        base_product = category_products[i]
                    else:
                        base_product = random.choice(category_products)
                    
                    # Gerar nome do produto
                    product_name = self.data_generator._generate_realistic_product_name(category)
                    
                    # Gerar preço
                    price = self.data_generator._generate_realistic_price_by_category(category)
                    original_price = self.data_generator._generate_original_price(price)
                    
                    # Criar produto
                    product = {
                        'name': product_name,
                        'description': self.data_generator._generate_realistic_description(product_name, category),
                        'price': price,
                        'original_price': original_price,
                        'category': self._get_product_category(product_name, category),
                        'restaurant_id': restaurant_id,
                        'image_url': f"https://example.com/products/{abs(hash(product_name))}.jpg",
                        'is_available': random.choice([True, True, True, False]),  # 75% disponível
                        'nutritional_info': self._generate_nutritional_info(product_name, category),
                        'allergens': self._generate_allergens(category),
                        'tags': self._generate_product_tags(product_name, category),
                        'preparation_time': self._generate_preparation_time(category),
                        'portion_size': self._generate_portion_size(category)
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao gerar produto para {restaurant_name}: {e}")
                    continue
            
            self.logger.debug(f"Gerados {len(products)} produtos para {restaurant_name}")
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair produtos para restaurante: {e}")
        
        return products
    
    def _get_category_products(self, category: str) -> List[str]:
        """Obtém produtos típicos de uma categoria"""
        return self.data_generator._get_category_products(category)
    
    def _get_product_category(self, product_name: str, restaurant_category: str) -> str:
        """Determina categoria do produto baseado no nome e categoria do restaurante"""
        # Mapeamento de palavras-chave para categorias
        product_categories = {
            'pizza': ['pizza', 'margherita', 'calabresa', 'portuguesa'],
            'hamburguer': ['burger', 'hamburguer', 'big mac', 'whopper'],
            'bebidas': ['suco', 'refrigerante', 'café', 'água', 'smoothie'],
            'doces': ['brigadeiro', 'sorvete', 'açaí', 'cupcake', 'chocolate'],
            'saladas': ['salada', 'caesar', 'verde', 'mix'],
            'massas': ['lasanha', 'fettuccine', 'macarrão', 'gnocchi'],
            'carnes': ['picanha', 'frango', 'carne', 'bife'],
            'peixes': ['salmão', 'bacalhau', 'peixe', 'camarão'],
            'vegetariano': ['quinoa', 'tofu', 'vegetariano', 'vegano']
        }
        
        product_lower = product_name.lower()
        
        # Verificar palavras-chave
        for category_key, keywords in product_categories.items():
            if any(keyword in product_lower for keyword in keywords):
                return category_key
        
        # Fallback para categoria do restaurante
        return restaurant_category
    
    def _generate_nutritional_info(self, product_name: str, category: str) -> str:
        """Gera informações nutricionais básicas"""
        nutritional_templates = {
            'pizza': f"Calorias: {random.randint(200, 400)} por fatia | Carboidratos: {random.randint(20, 35)}g | Proteínas: {random.randint(8, 15)}g",
            'hamburguer': f"Calorias: {random.randint(300, 600)} | Carboidratos: {random.randint(25, 45)}g | Proteínas: {random.randint(15, 30)}g",
            'saudável': f"Calorias: {random.randint(150, 350)} | Carboidratos: {random.randint(10, 25)}g | Proteínas: {random.randint(10, 20)}g | Fibras: {random.randint(3, 8)}g",
            'bebidas': f"Calorias: {random.randint(0, 150)} | Açúcares: {random.randint(0, 25)}g | Vitamina C: {random.randint(10, 100)}mg",
            'doces': f"Calorias: {random.randint(150, 400)} | Açúcares: {random.randint(15, 40)}g | Gorduras: {random.randint(5, 20)}g"
        }
        
        return nutritional_templates.get(category, f"Calorias: {random.randint(200, 400)} | Informações nutricionais disponíveis no estabelecimento")
    
    def _generate_allergens(self, category: str) -> str:
        """Gera informações sobre alérgenos"""
        allergen_mapping = {
            'pizza': ['Glúten', 'Leite', 'Ovos'],
            'hamburguer': ['Glúten', 'Leite', 'Ovos', 'Soja'],
            'japonesa': ['Peixe', 'Soja', 'Glúten'],
            'italiana': ['Glúten', 'Leite', 'Ovos'],
            'doces': ['Leite', 'Ovos', 'Glúten', 'Amendoim'],
            'bebidas': []
        }
        
        possible_allergens = allergen_mapping.get(category, ['Glúten', 'Leite'])
        
        if not possible_allergens:
            return "Não contém alérgenos declarados"
        
        # Selecionar alguns alérgenos aleatoriamente
        selected_allergens = random.sample(possible_allergens, min(random.randint(1, 3), len(possible_allergens)))
        
        return f"Contém: {', '.join(selected_allergens)}"
    
    def _generate_product_tags(self, product_name: str, category: str) -> List[str]:
        """Gera tags para o produto"""
        tag_mapping = {
            'pizza': ['Italiana', 'Assada', 'Tradicional', 'Gourmet'],
            'hamburguer': ['Grelhado', 'Artesanal', 'Suculento', 'Crocante'],
            'japonesa': ['Fresco', 'Oriental', 'Tradicional', 'Premium'],
            'saudável': ['Natural', 'Orgânico', 'Fitness', 'Integral'],
            'doces': ['Cremoso', 'Artesanal', 'Doce', 'Irresistível'],
            'bebidas': ['Refrescante', 'Natural', 'Gelado', 'Energético']
        }
        
        available_tags = tag_mapping.get(category, ['Delicioso', 'Especial', 'Tradicional'])
        
        # Adicionar tags específicas baseadas no nome do produto
        if 'gourmet' in product_name.lower():
            available_tags.append('Gourmet')
        if 'especial' in product_name.lower():
            available_tags.append('Especial')
        if 'premium' in product_name.lower():
            available_tags.append('Premium')
        
        return random.sample(available_tags, min(2, len(available_tags)))
    
    def _generate_preparation_time(self, category: str) -> str:
        """Gera tempo de preparo baseado na categoria"""
        time_ranges = {
            'pizza': (15, 30),
            'hamburguer': (10, 20),
            'japonesa': (15, 25),
            'italiana': (20, 35),
            'saudável': (5, 15),
            'doces': (5, 10),
            'bebidas': (2, 5)
        }
        
        min_time, max_time = time_ranges.get(category, (10, 25))
        prep_time = random.randint(min_time, max_time)
        
        return f"{prep_time} min"
    
    def _generate_portion_size(self, category: str) -> str:
        """Gera tamanho da porção baseado na categoria"""
        portion_mapping = {
            'pizza': ['Pequena (4 fatias)', 'Média (6 fatias)', 'Grande (8 fatias)', 'Família (12 fatias)'],
            'hamburguer': ['Individual', 'Duplo', 'Triplo'],
            'japonesa': ['8 peças', '12 peças', '16 peças'],
            'italiana': ['Pequena', 'Média', 'Grande'],
            'saudável': ['300g', '400g', '500g'],
            'doces': ['Individual', 'Para 2 pessoas', 'Família'],
            'bebidas': ['300ml', '500ml', '700ml', '1L']
        }
        
        portions = portion_mapping.get(category, ['Individual', 'Pequena', 'Média', 'Grande'])
        return random.choice(portions)
    
    async def run_parallel_extraction(self, categories: List[str], 
                                    restaurants_per_category: int = 50,
                                    products_per_restaurant: int = 10) -> Dict[str, Any]:
        """Executa extração paralela para múltiplas categorias"""
        start_time = datetime.now()
        
        self.logger.info(f"Iniciando extração paralela para {len(categories)} categorias")
        
        all_restaurants = []
        all_products = []
        
        try:
            # Processar cada categoria
            for category in categories:
                self.logger.info(f"Processando categoria: {category}")
                
                # Gerar restaurantes para a categoria
                restaurants = self.data_generator._generate_restaurants_for_category(
                    category, restaurants_per_category
                )
                
                # Simular salvamento para obter IDs
                restaurant_results = self.db_manager._save_restaurants_to_mysql(restaurants)
                
                # Obter restaurantes salvos com IDs
                saved_restaurants = self.db_manager._load_existing_restaurants_mysql()
                category_restaurants = [r for r in saved_restaurants if r['category'] == category]
                
                # Gerar produtos para cada restaurante
                for restaurant in category_restaurants:
                    products = await self.extract_products_for_restaurant(
                        restaurant, products_per_restaurant
                    )
                    all_products.extend(products)
                
                all_restaurants.extend(category_restaurants)
                
                self.logger.info(f"Categoria {category} processada: {len(category_restaurants)} restaurantes, {len(all_products)} produtos")
            
            # Salvar todos os produtos
            if all_products:
                product_results = self.db_manager._save_products_to_mysql(all_products)
            else:
                product_results = {'inserted': 0, 'updated': 0, 'errors': 0}
            
            # Calcular estatísticas finais
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            results = {
                'success': True,
                'total_time': total_time,
                'categories_processed': len(categories),
                'restaurants': {
                    'total': len(all_restaurants),
                    'by_category': {cat: len([r for r in all_restaurants if r['category'] == cat]) 
                                  for cat in categories}
                },
                'products': {
                    'total': len(all_products),
                    'inserted': product_results['inserted'],
                    'updated': product_results['updated'],
                    'errors': product_results['errors']
                },
                'performance': {
                    'restaurants_per_second': len(all_restaurants) / total_time if total_time > 0 else 0,
                    'products_per_second': len(all_products) / total_time if total_time > 0 else 0
                }
            }
            
            self.logger.info(f"Extração paralela concluída em {total_time:.2f}s")
            self.logger.info(f"Total: {len(all_restaurants)} restaurantes, {len(all_products)} produtos")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na extração paralela: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'total_time': (datetime.now() - start_time).total_seconds(),
                'categories_processed': 0,
                'restaurants': {'total': 0},
                'products': {'total': 0}
            }
    
    async def process_single_category(self, category: str, 
                                    restaurants_per_category: int = 50,
                                    products_per_restaurant: int = 10) -> Dict[str, Any]:
        """Processa uma única categoria"""
        return await self.run_parallel_extraction(
            [category], restaurants_per_category, products_per_restaurant
        )