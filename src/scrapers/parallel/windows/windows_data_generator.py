#!/usr/bin/env python3
"""
Windows Data Generator - Geração de dados realísticos para scraping paralelo
"""

import random
import hashlib
from typing import Dict, List, Any
from datetime import datetime


class WindowsDataGenerator:
    """Gerador de dados realísticos para extração paralela no Windows"""
    
    def __init__(self):
        self.restaurant_names_by_category = {
            'pizza': [
                'Pizzaria Bella Vista', 'Dom Pietro Pizza', 'Pizza Express SP', 'Nonna Maria',
                'Pizzaria da Esquina', 'Pizza Palace', 'Margherita Pizzeria', 'Tony\'s Pizza',
                'Pizza Romana', 'Forno di Napoli', 'Pizza & Vino', 'La Bela Pizza'
            ],
            'hamburguer': [
                'Burger King Brasil', 'McDonald\'s', 'Burger House', 'Smash Burger',
                'The Burger Joint', 'Classic Burger', 'Gourmet Burger', 'Big Burger',
                'Burger Station', 'Prime Burger', 'Artisan Burger', 'Burger Palace'
            ],
            'japonesa': [
                'Sushi Zen', 'Temaki House', 'Sakura Sushi', 'Tokyo Express',
                'Sushi Bar', 'Yamato Sushi', 'Koi Sushi', 'Nipon Sushi',
                'Sushi Time', 'Hokkaido Sushi', 'Wasabi Sushi', 'Fuji Sushi'
            ],
            'italiana': [
                'Cantina Italiana', 'Nonna Rosa', 'Trattoria Milano', 'Pasta & Basta',
                'Il Forno', 'Bella Italia', 'Osteria del Centro', 'Mamma Mia',
                'Ristorante Toscana', 'La Tavola', 'Dolce Vita', 'Casa Italiana'
            ],
            'brasileira': [
                'Boteco do João', 'Churrascaria Gaúcha', 'Comida Caseira', 'Sabor Mineiro',
                'Cantina da Vovó', 'Tempero Brasileiro', 'Casa do Norte', 'Fogão a Lenha',
                'Tradição Brasileira', 'Sabores do Brasil', 'Cozinha Caipira', 'Rancho Alegre'
            ],
            'chinesa': [
                'China Express', 'Dragão Dourado', 'Panda House', 'Great Wall',
                'China Palace', 'Golden Dragon', 'Lotus Garden', 'Bamboo House',
                'Orient Express', 'China Town', 'Red Dragon', 'Jade Garden'
            ],
            'mexicana': [
                'El Sombrero', 'Taco Bell', 'Azteca Restaurant', 'Chili\'s',
                'Casa Mexico', 'Mariachi', 'Viva Mexico', 'Cantina Mexicana',
                'Señor Frog\'s', 'Hacienda', 'Guadalajara', 'Tierra Mexico'
            ],
            'árabe': [
                'Habib\'s', 'Arábia', 'Cedro do Líbano', 'Al Janiah',
                'Beirute', 'Petra', 'Oasis', 'Sahara',
                'Damascus', 'Aladdin', 'Sheik Palace', 'Sultão'
            ],
            'saudável': [
                'Green Life', 'Fit Food', 'Vida Saudável', 'Natural Gourmet',
                'Organic Kitchen', 'Salad Bar', 'Healthy Choice', 'Fresh Market',
                'Pure Life', 'Clean Eating', 'Detox Kitchen', 'Vegan Delights'
            ],
            'doces': [
                'Doce Sabor', 'Açaí da Hora', 'Gelateria Italiana', 'Cupcake House',
                'Chocolateria Cacau', 'Brigadeiro Gourmet', 'Sorveteria Polar', 'Doce Mania',
                'Confeitaria Central', 'Sugar Rush', 'Sweet Dreams', 'Candy Shop'
            ],
            'lanches': [
                'Lanche da Esquina', 'Hot Dog do Carlinhos', 'Sanduíche Mania', 'Quick Bite',
                'Lanchonete Central', 'Subway', 'Sandwich Shop', 'Bite Size',
                'Fast Food Express', 'Snack Bar', 'Quick Lunch', 'Grab & Go'
            ],
            'bebidas': [
                'Juice Bar', 'Café Central', 'Starbucks', 'Smoothie House',
                'Tropical Drinks', 'Fresh Juice', 'Café da Manhã', 'Drink Station',
                'Beverage Corner', 'Liquid Lounge', 'Refresh Bar', 'Hydration Station'
            ]
        }
        
        self.product_categories = {
            'pizza': ['Pizza Margherita', 'Pizza Calabresa', 'Pizza Portuguesa', 'Pizza Quatro Queijos'],
            'hamburguer': ['Big Mac', 'Whopper', 'Cheese Burger', 'Bacon Burger'],
            'japonesa': ['Sushi Salmão', 'Temaki Filadélfia', 'Yakisoba', 'Udon'],
            'italiana': ['Lasanha', 'Fettuccine Alfredo', 'Risotto', 'Gnocchi'],
            'brasileira': ['Feijoada', 'Picanha', 'Pão de Açúcar', 'Coxinha'],
            'chinesa': ['Frango Xadrez', 'Chop Suey', 'Rolinho Primavera', 'Macarrão Chow Mein'],
            'mexicana': ['Tacos', 'Burrito', 'Quesadilla', 'Nachos'],
            'árabe': ['Esfiha', 'Kebab', 'Homus', 'Tabule'],
            'saudável': ['Salada Caesar', 'Smoothie Verde', 'Wrap Integral', 'Quinoa Bowl'],
            'doces': ['Brigadeiro', 'Açaí', 'Sorvete', 'Cupcake'],
            'lanches': ['Sanduíche Natural', 'Hot Dog', 'Batata Frita', 'Milk Shake'],
            'bebidas': ['Suco de Laranja', 'Café Expresso', 'Refrigerante', 'Água Mineral']
        }
    
    def _get_restaurant_names_by_category(self, category: str) -> List[str]:
        """Retorna nomes de restaurantes por categoria"""
        return self.restaurant_names_by_category.get(category, [
            'Restaurante Genérico', 'Comida Boa', 'Sabor Especial', 'Delicias da Casa'
        ])
    
    def _generate_restaurants_for_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Gera restaurantes realísticos para uma categoria"""
        restaurants = []
        names = self._get_restaurant_names_by_category(category)
        
        for i in range(limit):
            # Escolher nome base
            base_name = random.choice(names)
            
            # Adicionar variação se necessário
            if i >= len(names):
                variation = random.choice(['Express', 'Delivery', 'Gourmet', 'Premium', 'Plus', 'Prime'])
                restaurant_name = f"{base_name} {variation}"
            else:
                restaurant_name = base_name
            
            # Gerar dados do restaurante
            restaurant = {
                'name': restaurant_name,
                'category': category,
                'rating': round(random.uniform(3.5, 4.9), 1),
                'delivery_fee': self._generate_delivery_fee(),
                'delivery_time': f"{random.randint(25, 60)} min",
                'address': self._generate_address(),
                'tags': self._generate_tags(category),
                'is_open': random.choice([True, True, True, False]),  # 75% aberto
                'image_url': f"https://example.com/restaurants/{hashlib.md5(restaurant_name.encode()).hexdigest()}.jpg"
            }
            
            restaurants.append(restaurant)
        
        return restaurants
    
    def _generate_realistic_product_name(self, category: str) -> str:
        """Gera nome de produto realístico baseado na categoria"""
        base_products = self.product_categories.get(category, ['Prato Especial', 'Combo', 'Delícia'])
        
        base_name = random.choice(base_products)
        
        # Adicionar variações ocasionais
        if random.random() < 0.3:  # 30% chance de variação
            variations = ['Especial', 'Gourmet', 'Premium', 'da Casa', 'Tradicional', 'Completo']
            variation = random.choice(variations)
            return f"{base_name} {variation}"
        
        return base_name
    
    def _generate_realistic_description(self, product_name: str, category: str) -> str:
        """Gera descrição realística do produto"""
        descriptions = {
            'pizza': f"Deliciosa {product_name} com ingredientes frescos e massa artesanal. Assada no forno a lenha.",
            'hamburguer': f"Suculento {product_name} com carne 100% bovina, acompanhado de batatas fritas crocantes.",
            'japonesa': f"Autêntico {product_name} preparado pelo chef japonês com ingredientes importados.",
            'italiana': f"Tradicional {product_name} com receita da nonna, servido com molho especial da casa.",
            'brasileira': f"Saboroso {product_name} preparado com temperos regionais e ingredientes selecionados.",
            'chinesa': f"Exótico {product_name} com sabores orientais e vegetais frescos, preparado no wok.",
            'mexicana': f"Picante {product_name} com especiarias mexicanas e molho apimentado especial.",
            'árabe': f"Aromático {product_name} com especiarias do Oriente Médio e receita tradicional.",
            'saudável': f"Nutritivo {product_name} com ingredientes orgânicos e baixo teor calórico.",
            'doces': f"Irresistível {product_name} preparado com ingredientes premium e muito amor.",
            'lanches': f"Prático {product_name} ideal para um lanche rápido e saboroso.",
            'bebidas': f"Refrescante {product_name} preparado com frutas frescas e ingredientes naturais."
        }
        
        return descriptions.get(category, f"Delicioso {product_name} preparado com ingredientes selecionados.")
    
    def _generate_realistic_price_by_category(self, category: str) -> float:
        """Gera preço realístico baseado na categoria"""
        price_ranges = {
            'pizza': (25.0, 65.0),
            'hamburguer': (18.0, 45.0),
            'japonesa': (35.0, 85.0),
            'italiana': (28.0, 70.0),
            'brasileira': (22.0, 55.0),
            'chinesa': (20.0, 50.0),
            'mexicana': (25.0, 60.0),
            'árabe': (15.0, 40.0),
            'saudável': (20.0, 50.0),
            'doces': (8.0, 25.0),
            'lanches': (10.0, 30.0),
            'bebidas': (5.0, 20.0)
        }
        
        min_price, max_price = price_ranges.get(category, (10.0, 40.0))
        return round(random.uniform(min_price, max_price), 2)
    
    def _generate_delivery_fee(self) -> float:
        """Gera taxa de entrega realística"""
        fees = [0.0, 2.99, 3.99, 4.99, 5.99, 6.99, 7.99]
        return random.choice(fees)
    
    def _generate_address(self) -> str:
        """Gera endereço realístico"""
        streets = [
            'Rua das Flores', 'Av. Paulista', 'Rua Augusta', 'Rua Oscar Freire',
            'Av. Faria Lima', 'Rua da Consolação', 'Av. Rebouças', 'Rua Haddock Lobo',
            'Av. Ibirapuera', 'Rua Teodoro Sampaio', 'Av. Brasil', 'Rua XV de Novembro'
        ]
        
        street = random.choice(streets)
        number = random.randint(100, 2000)
        
        return f"{street}, {number} - São Paulo, SP"
    
    def _generate_tags(self, category: str) -> List[str]:
        """Gera tags relevantes para a categoria"""
        tag_mapping = {
            'pizza': ['Italiana', 'Forno a Lenha', 'Delivery', 'Tradicional'],
            'hamburguer': ['Fast Food', 'Gourmet', 'American', 'Artesanal'],
            'japonesa': ['Sushi', 'Oriental', 'Temaki', 'Frutos do Mar'],
            'italiana': ['Massas', 'Mediterrânea', 'Vinho', 'Tradicional'],
            'brasileira': ['Caseira', 'Regional', 'Churrasco', 'Mineira'],
            'chinesa': ['Oriental', 'Wok', 'Vegetariana', 'Agridoce'],
            'mexicana': ['Picante', 'Tex-Mex', 'Apimentada', 'Latina'],
            'árabe': ['Mediterrânea', 'Especiarias', 'Halal', 'Tradicional'],
            'saudável': ['Fitness', 'Orgânica', 'Vegetariana', 'Diet'],
            'doces': ['Sobremesas', 'Artesanal', 'Gelatos', 'Confeitaria'],
            'lanches': ['Rápido', 'Prático', 'Casual', 'Sanduíches'],
            'bebidas': ['Natural', 'Refrescante', 'Vitaminas', 'Sucos']
        }
        
        available_tags = tag_mapping.get(category, ['Comida', 'Delivery', 'Gourmet'])
        return random.sample(available_tags, min(2, len(available_tags)))
    
    def _fix_incorrect_category(self, original_category: str) -> str:
        """Corrige categorias incorretas ou normaliza nomes"""
        category_mapping = {
            'pizzas': 'pizza',
            'hamburguers': 'hamburguer',
            'hamburger': 'hamburguer',
            'burgers': 'hamburguer',
            'japonês': 'japonesa',
            'japa': 'japonesa',
            'italiano': 'italiana',
            'brazil': 'brasileira',
            'brazilian': 'brasileira',
            'chinese': 'chinesa',
            'mexican': 'mexicana',
            'arab': 'árabe',
            'arabic': 'árabe',
            'healthy': 'saudável',
            'fit': 'saudável',
            'sweets': 'doces',
            'desserts': 'doces',
            'snacks': 'lanches',
            'drinks': 'bebidas'
        }
        
        # Normalizar para lowercase
        normalized = original_category.lower().strip()
        
        # Aplicar mapeamento se existir
        return category_mapping.get(normalized, normalized)
    
    def _get_category_products(self, category: str) -> List[str]:
        """Retorna produtos típicos de uma categoria"""
        return self.product_categories.get(category, ['Prato Especial', 'Combo do Dia', 'Delícia da Casa'])
    
    def _generate_original_price(self, current_price: float) -> float:
        """Gera preço original (antes do desconto) se aplicável"""
        if random.random() < 0.3:  # 30% chance de ter desconto
            discount = random.uniform(0.1, 0.3)  # 10% a 30% de desconto
            return round(current_price / (1 - discount), 2)
        return current_price
    
    def get_supported_categories(self) -> List[str]:
        """Retorna lista de categorias suportadas"""
        return list(self.restaurant_names_by_category.keys())