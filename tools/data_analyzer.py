#!/usr/bin/env python3
"""
Ferramenta para análise dos dados coletados pelo iFood Scraper
Gera relatórios e estatísticas dos dados extraídos
"""

import os
import sys
import csv
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DataAnalyzer:
    """Analisador de dados do iFood Scraper"""
    
    def __init__(self, data_dir="./data"):
        self.data_dir = Path(data_dir)
        self.categories_dir = self.data_dir / "categories"
        self.restaurants_dir = self.data_dir / "restaurants"
        self.products_dir = self.data_dir / "products"
        self.categories_file = self.categories_dir / "ifood_data_categories.csv"
        self.metadata_file = self.data_dir / "ifood_data_metadata.json"
    
    def analyze_categories(self):
        """Analisa dados das categorias"""
        print("=== Análise de Categorias ===")
        
        if not self.categories_file.exists():
            print("❌ Arquivo de categorias não encontrado")
            return
        
        categories = []
        with open(self.categories_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            categories = list(reader)
        
        print(f"📊 Total de categorias: {len(categories)}")
        
        # Análise por cidade
        cities = Counter(cat['city'] for cat in categories)
        print(f"🏙️  Cidades cobertas: {len(cities)}")
        
        for city, count in cities.most_common():
            print(f"   {city}: {count} categorias")
        
        # Categorias mais populares
        print(f"\n📋 Todas as categorias:")
        for cat in categories:
            print(f"   • {cat['name']}")
    
    def analyze_restaurants(self):
        """Analisa dados dos restaurantes"""
        print("\n=== Análise de Restaurantes ===")
        
        restaurant_files = list(self.restaurants_dir.glob("ifood_data_restaurantes_*.csv"))
        
        if not restaurant_files:
            print("❌ Nenhum arquivo de restaurantes encontrado")
            return
        
        total_restaurants = 0
        categories_data = defaultdict(list)
        ratings = []
        delivery_fees = []
        
        for file_path in restaurant_files:
            category = file_path.stem.replace("ifood_data_restaurantes_", "").replace("_", " ").title()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                restaurants = list(reader)
                
                categories_data[category] = restaurants
                total_restaurants += len(restaurants)
                
                # Coleta ratings para análise
                for rest in restaurants:
                    try:
                        rating = float(rest.get('avaliacao', 0))
                        if rating > 0:
                            ratings.append(rating)
                    except (ValueError, TypeError):
                        pass
                    
                    # Coleta taxas de entrega
                    fee = rest.get('taxa_entrega', '')
                    if fee and fee != 'Não informado':
                        delivery_fees.append(fee)
        
        print(f"📊 Total de restaurantes: {total_restaurants}")
        print(f"📂 Categorias com dados: {len(categories_data)}")
        
        # Estatísticas por categoria
        print(f"\n🍽️  Restaurantes por categoria:")
        for category, restaurants in sorted(categories_data.items(), 
                                          key=lambda x: len(x[1]), reverse=True):
            print(f"   {category}: {len(restaurants)} restaurantes")
        
        # Análise de ratings
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"\n⭐ Análise de Avaliações:")
            print(f"   Média geral: {avg_rating:.2f}")
            print(f"   Maior rating: {max(ratings):.1f}")
            print(f"   Menor rating: {min(ratings):.1f}")
            
            # Distribuição de ratings
            rating_dist = Counter(f"{r:.1f}" for r in ratings)
            print(f"   Distribuição:")
            for rating, count in sorted(rating_dist.items(), reverse=True):
                percentage = (count / len(ratings)) * 100
                print(f"     {rating}⭐: {count} ({percentage:.1f}%)")
        
        # Análise de taxas de entrega
        if delivery_fees:
            gratis_count = sum(1 for fee in delivery_fees if 'grátis' in fee.lower())
            pago_count = len(delivery_fees) - gratis_count
            
            print(f"\n💰 Análise de Taxas de Entrega:")
            print(f"   Grátis: {gratis_count} ({(gratis_count/len(delivery_fees)*100):.1f}%)")
            print(f"   Pago: {pago_count} ({(pago_count/len(delivery_fees)*100):.1f}%)")
    
    def analyze_urls(self):
        """Analisa disponibilidade de URLs dos restaurantes"""
        print("\n=== Análise de URLs ===")
        
        restaurant_files = list(self.restaurants_dir.glob("ifood_data_restaurantes_*.csv"))
        
        total_restaurants = 0
        restaurants_with_url = 0
        
        for file_path in restaurant_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for restaurant in reader:
                    total_restaurants += 1
                    url = restaurant.get('url', '').strip()
                    if url and url != 'None' and url != '':
                        restaurants_with_url += 1
        
        if total_restaurants > 0:
            percentage = (restaurants_with_url / total_restaurants) * 100
            print(f"🔗 Restaurantes com URL: {restaurants_with_url}/{total_restaurants} ({percentage:.1f}%)")
            
            if restaurants_with_url == 0:
                print("⚠️  Nenhuma URL foi capturada. Verifique a implementação de extração de URLs.")
            elif percentage < 50:
                print("⚠️  Baixa taxa de captura de URLs. Considere melhorar os seletores.")
        else:
            print("❌ Nenhum restaurante encontrado")
    
    def analyze_products(self):
        """Analisa dados dos produtos"""
        print("\n=== Análise de Produtos ===")
        
        product_files = list(self.products_dir.glob("ifood_data_produtos_*.csv"))
        
        if not product_files:
            print("❌ Nenhum arquivo de produtos encontrado")
            return
        
        total_products = 0
        products_by_restaurant = {}
        prices = []
        categories_products = defaultdict(int)
        
        for file_path in product_files:
            restaurant_name = file_path.stem.replace("ifood_data_produtos_", "").replace("_", " ").title()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
                
                products_by_restaurant[restaurant_name] = len(products)
                total_products += len(products)
                
                # Coleta preços para análise
                for product in products:
                    try:
                        price_str = product.get('preco', '').replace('R$', '').replace(' ', '').replace(',', '.')
                        if price_str and price_str != 'Não informado':
                            price = float(price_str)
                            if 0 < price < 1000:  # Filtro básico
                                prices.append(price)
                    except (ValueError, TypeError):
                        pass
                    
                    # Conta categorias de produtos
                    category = product.get('categoria_produto', 'Não categorizado')
                    categories_products[category] += 1
        
        print(f"📊 Total de produtos: {total_products}")
        print(f"🏪 Restaurantes com produtos: {len(products_by_restaurant)}")
        
        # Top restaurantes por número de produtos
        print(f"\n🥇 Top restaurantes por variedade:")
        sorted_restaurants = sorted(products_by_restaurant.items(), key=lambda x: x[1], reverse=True)
        for restaurant, count in sorted_restaurants[:10]:
            print(f"   {restaurant}: {count} produtos")
        
        # Análise de preços
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"\n💰 Análise de Preços:")
            print(f"   Preço médio: R$ {avg_price:.2f}")
            print(f"   Preço mínimo: R$ {min(prices):.2f}")
            print(f"   Preço máximo: R$ {max(prices):.2f}")
            
            # Distribuição por faixas de preço
            faixas = {
                "Até R$ 10": sum(1 for p in prices if p <= 10),
                "R$ 10-20": sum(1 for p in prices if 10 < p <= 20),
                "R$ 20-50": sum(1 for p in prices if 20 < p <= 50),
                "Acima R$ 50": sum(1 for p in prices if p > 50)
            }
            
            print(f"\n📈 Distribuição por preço:")
            for faixa, count in faixas.items():
                percentage = (count / len(prices)) * 100
                print(f"   {faixa}: {count} ({percentage:.1f}%)")
        
        # Categorias mais comuns
        if categories_products:
            print(f"\n🏷️  Top categorias de produtos:")
            sorted_categories = sorted(categories_products.items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories[:10]:
                print(f"   {category}: {count} produtos")
    
    def show_metadata(self):
        """Mostra metadados do banco de dados"""
        print("\n=== Metadados ===")
        
        if not self.metadata_file.exists():
            print("❌ Arquivo de metadados não encontrado")
            return
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        stats = metadata.get('statistics', {})
        
        for data_type, data_stats in stats.items():
            print(f"📊 {data_type.title()}:")
            print(f"   Total salvo: {data_stats.get('total_saved', 0)}")
            print(f"   Duplicados: {data_stats.get('total_duplicates', 0)}")
            print(f"   Última atualização: {data_stats.get('last_update', 'N/A')}")
        
        print(f"\n🗃️  Banco criado em: {metadata.get('created_at', 'N/A')}")
    
    def generate_report(self):
        """Gera relatório completo"""
        print("🚀 iFood Scraper - Relatório de Análise")
        print("=" * 50)
        print(f"📅 Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.analyze_categories()
        self.analyze_restaurants()
        self.analyze_urls()
        self.analyze_products()
        self.show_metadata()
        
        print("\n" + "=" * 50)
        print("✨ Análise concluída!")


def main():
    """Função principal"""
    analyzer = DataAnalyzer()
    
    try:
        analyzer.generate_report()
    except KeyboardInterrupt:
        print("\n⏹️  Análise interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")


if __name__ == "__main__":
    main()