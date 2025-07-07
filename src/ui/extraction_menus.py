#!/usr/bin/env python3
"""
Menus de Extração - Categorias, Restaurantes, Produtos
"""

import platform
from pathlib import Path
from typing import Dict, List, Any

from src.scrapers.category_scraper import CategoryScraper
from src.scrapers.restaurant_scraper import RestaurantScraper
from src.scrapers.product_scraper import ProductScraper
from .base_menu import BaseMenu


class ExtractionMenus(BaseMenu):
    """Menus para extração de dados"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Extração", session_stats, data_dir)
    
    def menu_extract_categories(self):
        """Menu para extração de categorias"""
        print("\n🏷️  EXTRAÇÃO DE CATEGORIAS")
        print("═" * 50)
        
        city = input("Digite a cidade [Birigui]: ").strip() or "Birigui"
        
        print(f"\n🔄 Extraindo categorias de {city}...")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                scraper = CategoryScraper(city=city)
                result = scraper.run(p)
                
                if result['success']:
                    self.session_stats['categories_extracted'] += result['categories_found']
                    print(f"✅ {result['categories_found']} categorias extraídas com sucesso!")
                    print(f"📊 Novas: {result['new_saved']}, Duplicadas: {result['duplicates']}")
                    
                    # Mostra algumas categorias
                    if result['categories']:
                        print("\n📋 Primeiras 5 categorias:")
                        for i, cat in enumerate(result['categories'][:5]):
                            print(f"  {i+1}. {cat.name}")
                else:
                    print(f"❌ Erro: {result['error']}")
                    
        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            print(f"❌ Erro: {e}")
        
        self.pause()
    
    def menu_extract_restaurants(self):
        """Menu para extração de restaurantes"""
        print("\n🏪 EXTRAÇÃO DE RESTAURANTES")
        print("═" * 50)
        
        # Verificar se há categorias no banco de dados
        try:
            from src.database.database_adapter import get_database_manager
            db = get_database_manager()
            categories = db.get_categories("Birigui")
        except Exception as e:
            self.logger.error(f"Erro ao acessar banco: {e}")
            categories = []
        
        if not categories:
            print("❌ Nenhuma categoria encontrada!")
            print("💡 Execute primeiro a extração de categorias (opção 1)")
            self.pause()
            return
        
        # Mostra categorias disponíveis
        print(f"\n📋 {len(categories)} categorias disponíveis:")
        for i, cat in enumerate(categories[:10]):
            print(f"  {i+1}. {cat.get('name', 'N/A')}")
        
        if len(categories) > 10:
            print(f"  ... e mais {len(categories) - 10} categorias")
        
        choice = input(f"\nOpções:\n1. Extrair TODAS as categorias\n2. Escolher categoria específica\n3. Voltar\nEscolha: ").strip()
        
        if choice == "1":
            self._extract_all_restaurants(categories)
        elif choice == "2":
            self._extract_specific_restaurant(categories)
        elif choice == "3":
            return
        else:
            self.show_invalid_option()
    
    def menu_extract_products(self):
        """Menu para extração de produtos"""
        print("\n🍕 EXTRAÇÃO DE PRODUTOS")
        print("═" * 50)
        
        # Verificar se há restaurantes
        restaurants_dir = self.data_dir / "restaurants"
        if not restaurants_dir.exists() or not list(restaurants_dir.glob("*.csv")):
            print("❌ Nenhum restaurante encontrado!")
            print("💡 Execute primeiro a extração de restaurantes (opção 2)")
            self.pause()
            return
        
        # Lista arquivos de restaurantes
        restaurant_files = list(restaurants_dir.glob("*.csv"))
        print(f"\n📋 {len(restaurant_files)} arquivos de restaurantes encontrados:")
        
        for i, file in enumerate(restaurant_files[:5]):
            print(f"  {i+1}. {file.stem}")
        
        if len(restaurant_files) > 5:
            print(f"  ... e mais {len(restaurant_files) - 5} arquivos")
        
        choice = input(f"\nOpções:\n1. Extrair produtos de TODOS os restaurantes\n2. Escolher arquivo específico\n3. Voltar\nEscolha: ").strip()
        
        if choice == "1":
            self._extract_all_products(restaurant_files)
        elif choice == "2":
            self._extract_specific_products(restaurant_files)
        elif choice == "3":
            return
        else:
            self.show_invalid_option()
    
    def _extract_all_restaurants(self, categories):
        """Extrai restaurantes de todas as categorias"""
        print(f"\n🔄 Extraindo restaurantes de {len(categories)} categorias...")
        
        confirm = input("⚠️  Isso pode demorar bastante. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            from playwright.sync_api import sync_playwright
            from src.scrapers.restaurant_scraper import RestaurantScraper
            
            total_restaurants = 0
            successful_categories = 0
            
            with sync_playwright() as p:
                scraper = RestaurantScraper(city="Birigui")
                
                for i, category in enumerate(categories, 1):
                    print(f"\n📁 Processando categoria {i}/{len(categories)}: {category.get('name')}")
                    
                    result = scraper.run_for_category(
                        p,
                        category_url=category.get('url', ''),
                        category_name=category.get('name', '')
                    )
                    
                    if result['success']:
                        restaurants_found = result['restaurants_found']
                        total_restaurants += restaurants_found
                        successful_categories += 1
                        print(f"✅ {restaurants_found} restaurantes extraídos de {category.get('name')}")
                    else:
                        print(f"❌ Erro em {category.get('name')}: {result['error']}")
                
                self.session_stats['restaurants_extracted'] += total_restaurants
                print(f"\n🎯 Resumo final:")
                print(f"  📁 Categorias processadas: {successful_categories}/{len(categories)}")
                print(f"  🏪 Total de restaurantes: {total_restaurants}")
                    
        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            print(f"❌ Erro: {e}")
        
        self.pause()
    
    def _extract_specific_restaurant(self, categories):
        """Extrai restaurantes de categoria específica"""
        print("\n🏪 Extração específica de restaurantes")
        
        # Mostra categorias numeradas
        print(f"\n📋 Escolha uma categoria:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat.get('name', 'N/A')}")
        
        try:
            choice = input(f"\nDigite o número da categoria (1-{len(categories)}): ").strip()
            if not choice.isdigit():
                print("❌ Número inválido!")
                self.pause()
                return
                
            choice_num = int(choice)
            if choice_num < 1 or choice_num > len(categories):
                print("❌ Número fora do intervalo!")
                self.pause()
                return
            
            selected_category = categories[choice_num - 1]
            print(f"\n🔄 Extraindo restaurantes da categoria: {selected_category.get('name')}")
            
            # Usar RestaurantScraper com playwright
            from playwright.sync_api import sync_playwright
            from src.scrapers.restaurant_scraper import RestaurantScraper
            
            with sync_playwright() as p:
                scraper = RestaurantScraper(city="Birigui")
                # Usa run_for_category com URL e nome da categoria
                result = scraper.run_for_category(
                    p, 
                    category_url=selected_category.get('url', ''),
                    category_name=selected_category.get('name', '')
                )
                
                if result['success']:
                    self.session_stats['restaurants_extracted'] += result['restaurants_found']
                    print(f"✅ {result['restaurants_found']} restaurantes extraídos!")
                    print(f"📊 Novos: {result['new_saved']}, Duplicados: {result['duplicates']}")
                else:
                    print(f"❌ Erro: {result['error']}")
                    
        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            print(f"❌ Erro: {e}")
        
        self.pause()
    
    def _extract_all_products(self, restaurant_files):
        """Extrai produtos de todos os restaurantes"""
        print(f"\n🔄 Extraindo produtos de {len(restaurant_files)} arquivos...")
        
        confirm = input("⚠️  Isso pode demorar muito tempo. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            from playwright.sync_api import sync_playwright
            from src.scrapers.product_scraper import ProductScraper
            import csv
            
            total_products = 0
            
            with sync_playwright() as p:
                scraper = ProductScraper(city="Birigui")
                
                for i, restaurant_file in enumerate(restaurant_files, 1):
                    print(f"\n📁 Processando arquivo {i}/{len(restaurant_files)}: {restaurant_file.name}")
                    
                    # Lê restaurantes do arquivo
                    restaurants = []
                    try:
                        with open(restaurant_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            restaurants = list(reader)
                    except Exception as e:
                        print(f"❌ Erro ao ler {restaurant_file.name}: {e}")
                        continue
                    
                    print(f"📊 {len(restaurants)} restaurantes em {restaurant_file.name}")
                    
                    for j, restaurant in enumerate(restaurants, 1):
                        restaurant_name = restaurant.get('name', 'N/A')
                        restaurant_url = restaurant.get('url', '')
                        restaurant_id = restaurant.get('id', '')
                        
                        print(f"  📍 {j}/{len(restaurants)}: {restaurant_name}")
                        
                        if not restaurant_url:
                            print(f"    ⚠️  URL não encontrada")
                            continue
                        
                        result = scraper.run_for_restaurant(
                            p,
                            restaurant_url=restaurant_url,
                            restaurant_name=restaurant_name,
                            restaurant_id=restaurant_id
                        )
                        
                        if result['success']:
                            products_found = result['products_found']
                            total_products += products_found
                            print(f"    ✅ {products_found} produtos")
                        else:
                            print(f"    ❌ Erro: {result['error'][:50]}...")
            
            self.session_stats['products_extracted'] += total_products
            print(f"\n🎯 Resumo final: {total_products} produtos extraídos de {len(restaurant_files)} arquivos")
                    
        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            print(f"❌ Erro: {e}")
        
        self.pause()
    
    def _extract_specific_products(self, restaurant_files):
        """Extrai produtos de arquivo específico"""
        print("\n🍕 Extração específica de produtos")
        
        # Mostra arquivos numerados
        print(f"\n📋 Escolha um arquivo:")
        for i, file in enumerate(restaurant_files, 1):
            print(f"  {i}. {file.stem}")
        
        try:
            choice = input(f"\nDigite o número do arquivo (1-{len(restaurant_files)}): ").strip()
            if not choice.isdigit():
                print("❌ Número inválido!")
                self.pause()
                return
                
            choice_num = int(choice)
            if choice_num < 1 or choice_num > len(restaurant_files):
                print("❌ Número fora do intervalo!")
                self.pause()
                return
            
            selected_file = restaurant_files[choice_num - 1]
            print(f"\n🔄 Extraindo produtos de: {selected_file.name}")
            
            from playwright.sync_api import sync_playwright
            from src.scrapers.product_scraper import ProductScraper
            import csv
            
            # Lê restaurantes do arquivo CSV
            restaurants = []
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    restaurants = list(reader)
            except Exception as e:
                print(f"❌ Erro ao ler arquivo: {e}")
                self.pause()
                return
            
            if not restaurants:
                print("❌ Nenhum restaurante encontrado no arquivo!")
                self.pause()
                return
            
            print(f"📊 Encontrados {len(restaurants)} restaurantes no arquivo")
            total_products = 0
            
            with sync_playwright() as p:
                scraper = ProductScraper(city="Birigui")
                
                for i, restaurant in enumerate(restaurants, 1):
                    restaurant_name = restaurant.get('name', 'N/A')
                    restaurant_url = restaurant.get('url', '')
                    restaurant_id = restaurant.get('id', '')
                    
                    print(f"\n📍 Processando restaurante {i}/{len(restaurants)}: {restaurant_name}")
                    
                    if not restaurant_url:
                        print(f"⚠️  URL não encontrada para {restaurant_name}")
                        continue
                    
                    result = scraper.run_for_restaurant(
                        p,
                        restaurant_url=restaurant_url,
                        restaurant_name=restaurant_name,
                        restaurant_id=restaurant_id
                    )
                    
                    if result['success']:
                        products_found = result['products_found']
                        total_products += products_found
                        print(f"✅ {products_found} produtos extraídos de {restaurant_name}")
                    else:
                        print(f"❌ Erro em {restaurant_name}: {result['error']}")
                
                self.session_stats['products_extracted'] += total_products
                print(f"\n🎯 Resumo: {total_products} produtos extraídos de {len(restaurants)} restaurantes")
                    
        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            print(f"❌ Erro: {e}")
        
        self.pause()