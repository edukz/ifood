#!/usr/bin/env python3
"""
Sistema de simulação realística para demonstrar funcionalidades
quando dependências do Playwright não estão disponíveis
"""

import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import csv

from src.utils.logger import setup_logger


class MockScraper:
    """Simulador realístico de extração de dados"""
    
    def __init__(self, city: str = "Birigui"):
        self.city = city
        self.logger = setup_logger(self.__class__.__name__)
        
        # Templates realísticos para geração de dados
        self.food_categories = [
            "Pizza", "Hambúrguer", "Japonesa", "Brasileira", "Italiana", 
            "Chinesa", "Mexicana", "Árabe", "Vegetariana", "Açaí",
            "Doces & Sobremesas", "Saudável", "Lanches", "Bebidas"
        ]
        
        self.restaurant_names = [
            "Pizzaria Bella Vita", "Burger King", "McDonald's", "Subway",
            "Sushi House", "Temakeria Zen", "Restaurante do João",
            "Churrascaria Gaúcha", "Cantina Italiana", "Taco Bell",
            "Açaí Mania", "Sorveteria Gelato", "Padaria Pão de Açúcar",
            "Lanchonete Central", "Hamburgueria Artesanal", "Pizza Express",
            "Comida Caseira da Vovó", "Restaurante Oriental", "Café Gourmet",
            "Doceria Delícias", "Bar e Petiscaria", "Pizzaria Romana"
        ]
        
        self.product_templates = {
            "Pizza": [
                "Pizza Margherita", "Pizza Calabresa", "Pizza Portuguesa", 
                "Pizza Quatro Queijos", "Pizza Pepperoni", "Pizza Vegetariana",
                "Pizza Frango Catupiry", "Pizza Bacon", "Pizza Napolitana"
            ],
            "Hambúrguer": [
                "X-Burger", "X-Salada", "X-Bacon", "X-Tudo", "Big Burger",
                "Cheese Burger", "Bacon Burger", "Veggie Burger", "Double Burger"
            ],
            "Japonesa": [
                "Sushi Salmão", "Temaki California", "Hot Roll", "Sashimi",
                "Combo Sushi", "Yakisoba", "Uramaki", "Gunkan", "Harumaki"
            ],
            "Açaí": [
                "Açaí 300ml", "Açaí 500ml", "Açaí Especial", "Açaí com Frutas",
                "Açaí Zero", "Smoothie de Açaí", "Tigela de Açaí", "Açaí Fitness"
            ]
        }
        
        self.realistic_prices = {
            "Pizza": (25.90, 89.90),
            "Hambúrguer": (15.90, 45.90),
            "Japonesa": (18.90, 120.00),
            "Açaí": (8.90, 35.90),
            "Bebidas": (3.50, 12.90),
            "Sobremesas": (6.90, 28.90)
        }
    
    def simulate_category_extraction(self, delay_factor: float = 1.0) -> Dict[str, Any]:
        """Simula extração de categorias"""
        self.logger.info(f"Simulando extração de categorias para {self.city}")
        
        # Simula tempo de carregamento
        time.sleep(0.5 * delay_factor)
        
        categories = []
        for i, category in enumerate(self.food_categories):
            categories.append({
                'id': f"cat_{i+1}",
                'name': category,
                'url': f"https://www.ifood.com.br/delivery/{self.city.lower()}/{category.lower()}",
                'city': self.city,
                'extracted_at': datetime.now().isoformat()
            })
        
        self.logger.info(f"Simulação concluída: {len(categories)} categorias")
        
        return {
            'success': True,
            'items_found': len(categories),
            'categories': categories,
            'simulation': True,
            'city': self.city
        }
    
    def simulate_restaurant_extraction(self, category: str, delay_factor: float = 1.0) -> Dict[str, Any]:
        """Simula extração de restaurantes"""
        self.logger.info(f"Simulando extração de restaurantes - categoria: {category}")
        
        # Simula tempo de carregamento
        time.sleep(random.uniform(1.0, 2.5) * delay_factor)
        
        num_restaurants = random.randint(8, 25)
        restaurants = []
        
        for i in range(num_restaurants):
            # Seleciona nome baseado na categoria
            if category.lower() in ['pizza', 'italiana']:
                name_pool = [n for n in self.restaurant_names if 'pizz' in n.lower() or 'ital' in n.lower()]
            elif category.lower() in ['japonesa', 'oriental']:
                name_pool = [n for n in self.restaurant_names if any(x in n.lower() for x in ['sushi', 'zen', 'oriental'])]
            else:
                name_pool = self.restaurant_names
            
            if not name_pool:
                name_pool = self.restaurant_names
                
            name = random.choice(name_pool)
            restaurant_id = f"rest_{category.lower()}_{i+1}"
            
            restaurants.append({
                'id': restaurant_id,
                'nome': f"{name} - {category}",
                'url': f"https://www.ifood.com.br/delivery/{self.city.lower()}/{restaurant_id}",
                'categoria': category,
                'city': self.city,
                'rating': round(random.uniform(3.8, 4.9), 1),
                'delivery_time': f"{random.randint(25, 60)}-{random.randint(60, 90)} min",
                'delivery_fee': f"R$ {random.uniform(2.99, 8.99):.2f}",
                'extracted_at': datetime.now().isoformat()
            })
        
        self.logger.info(f"Simulação concluída: {num_restaurants} restaurantes")
        
        return {
            'success': True,
            'items_found': num_restaurants,
            'restaurants': restaurants,
            'category': category,
            'simulation': True,
            'city': self.city
        }
    
    def simulate_product_extraction(self, restaurant_data: Dict[str, str], delay_factor: float = 1.0) -> Dict[str, Any]:
        """Simula extração de produtos de um restaurante"""
        restaurant_name = restaurant_data.get('nome', restaurant_data.get('name', 'Restaurante'))
        category = restaurant_data.get('categoria', 'Geral')
        
        self.logger.info(f"Simulando extração de produtos - {restaurant_name[:30]}")
        
        # Simula tempo de carregamento baseado no tamanho do restaurante
        time.sleep(random.uniform(0.5, 2.0) * delay_factor)
        
        # Número de produtos baseado na categoria
        if category.lower() in ['pizza', 'hambúrguer']:
            num_products = random.randint(15, 45)
        elif category.lower() in ['japonesa', 'italiana']:
            num_products = random.randint(20, 60)
        else:
            num_products = random.randint(8, 30)
        
        products = []
        
        # Seleciona template de produtos baseado na categoria
        if category in self.product_templates:
            product_names = self.product_templates[category]
            price_range = self.realistic_prices.get(category, (10.00, 50.00))
        else:
            product_names = self.product_templates["Pizza"]  # Default
            price_range = (8.90, 45.90)
        
        for i in range(num_products):
            base_name = random.choice(product_names)
            
            # Adiciona variações realísticas
            variations = ["", "Grande", "Pequena", "Média", "Especial", "Premium", "Light"]
            variation = random.choice(variations)
            
            product_name = f"{base_name} {variation}".strip()
            
            products.append({
                'id': f"prod_{restaurant_data.get('id', 'rest')}_{i+1}",
                'nome': product_name,
                'preco': round(random.uniform(price_range[0], price_range[1]), 2),
                'descricao': f"Delicioso {product_name.lower()} preparado com ingredientes frescos",
                'categoria': category,
                'restaurante': restaurant_name,
                'restaurante_id': restaurant_data.get('id', 'unknown'),
                'disponivel': random.choice([True, True, True, False]),  # 75% disponível
                'tempo_preparo': f"{random.randint(15, 45)} min",
                'extracted_at': datetime.now().isoformat()
            })
        
        self.logger.info(f"Simulação concluída: {num_products} produtos")
        
        return {
            'success': True,
            'items_found': num_products,
            'products': products,
            'restaurant': restaurant_name,
            'simulation': True,
            'city': self.city
        }
    
    def simulate_parallel_processing(self, restaurants: List[Dict[str, Any]], 
                                   max_workers: int = 3, 
                                   progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Simula processamento paralelo realístico"""
        self.logger.info(f"Iniciando simulação paralela: {len(restaurants)} restaurantes, {max_workers} workers")
        
        start_time = time.time()
        
        # Estatísticas
        stats = {
            'total_restaurants': len(restaurants),
            'total_products': 0,
            'completed_restaurants': 0,
            'failed_restaurants': 0,
            'processing_time': 0.0,
            'workers_used': min(max_workers, len(restaurants))
        }
        
        results = []
        
        # Simula processamento em batches (como workers paralelos)
        batch_size = max(1, len(restaurants) // max_workers)
        batches = [restaurants[i:i + batch_size] for i in range(0, len(restaurants), batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            self.logger.info(f"Processando batch {batch_idx + 1}/{len(batches)} ({len(batch)} restaurantes)")
            
            for restaurant in batch:
                try:
                    # Simula processamento com delay realístico
                    result = self.simulate_product_extraction(restaurant, delay_factor=0.1)
                    
                    if result['success']:
                        stats['completed_restaurants'] += 1
                        stats['total_products'] += result['items_found']
                        results.append(result)
                        
                        # Callback de progresso
                        if progress_callback:
                            progress = (stats['completed_restaurants'] / stats['total_restaurants']) * 100
                            progress_callback(restaurant['nome'], result['items_found'], progress)
                        
                        # Log de progresso a cada 10 restaurantes
                        if stats['completed_restaurants'] % 10 == 0:
                            progress = (stats['completed_restaurants'] / stats['total_restaurants']) * 100
                            self.logger.info(f"Progresso: {stats['completed_restaurants']}/{stats['total_restaurants']} ({progress:.1f}%)")
                    
                except Exception as e:
                    stats['failed_restaurants'] += 1
                    self.logger.warning(f"Falha ao simular {restaurant.get('nome', 'restaurante')}: {e}")
        
        stats['processing_time'] = time.time() - start_time
        
        # Log final
        self.logger.info(f"Simulação concluída:")
        self.logger.info(f"  Restaurantes processados: {stats['completed_restaurants']}/{stats['total_restaurants']}")
        self.logger.info(f"  Total de produtos simulados: {stats['total_products']}")
        self.logger.info(f"  Tempo total: {stats['processing_time']:.2f}s")
        self.logger.info(f"  Produtos por segundo: {stats['total_products'] / stats['processing_time']:.1f}")
        
        return {
            'success': True,
            'results': results,
            'stats': stats,
            'simulation': True,
            'simulation_note': 'Dados gerados para demonstração - Use scraper real para dados reais'
        }


def create_mock_data_files(output_dir: Path):
    """Cria arquivos de dados simulados para demonstração"""
    mock_scraper = MockScraper()
    
    # Simula categorias
    categories_result = mock_scraper.simulate_category_extraction()
    categories_file = output_dir / "mock_categorias.csv"
    
    with open(categories_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'url', 'city', 'extracted_at'])
        writer.writeheader()
        writer.writerows(categories_result['categories'])
    
    print(f"✅ Arquivo de categorias criado: {categories_file}")
    
    # Simula restaurantes para algumas categorias
    sample_categories = ["Pizza", "Hambúrguer", "Japonesa"]
    
    for category in sample_categories:
        restaurants_result = mock_scraper.simulate_restaurant_extraction(category)
        restaurants_file = output_dir / f"mock_restaurantes_{category.lower()}.csv"
        
        with open(restaurants_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'nome', 'url', 'categoria', 'city', 'rating', 
                'delivery_time', 'delivery_fee', 'extracted_at'
            ])
            writer.writeheader()
            writer.writerows(restaurants_result['restaurants'])
        
        print(f"✅ Arquivo de restaurantes criado: {restaurants_file}")


if __name__ == "__main__":
    # Demonstração
    mock = MockScraper()
    
    print("🎭 SISTEMA DE SIMULAÇÃO - DEMONSTRAÇÃO")
    print("=" * 50)
    
    # Simula extração de categorias
    print("\n1. Simulando extração de categorias...")
    cats = mock.simulate_category_extraction()
    print(f"   ✅ {cats['items_found']} categorias simuladas")
    
    # Simula extração de restaurantes
    print("\n2. Simulando extração de restaurantes...")
    rests = mock.simulate_restaurant_extraction("Pizza")
    print(f"   ✅ {rests['items_found']} restaurantes simulados")
    
    # Simula extração de produtos
    print("\n3. Simulando extração de produtos...")
    if rests['restaurants']:
        prods = mock.simulate_product_extraction(rests['restaurants'][0])
        print(f"   ✅ {prods['items_found']} produtos simulados")
    
    print("\n🎉 Simulação concluída com sucesso!")