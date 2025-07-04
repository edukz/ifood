import os
import csv
import json
import hashlib
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pathlib import Path
from src.config.settings import SETTINGS
from src.utils.logger import setup_logger


class DatabaseManager:
    """Gerenciador de banco de dados CSV com controle de duplicatas"""
    
    def __init__(self, db_name: str = "ifood_data"):
        self.logger = setup_logger("DatabaseManager")
        self.db_name = db_name
        
        # Diretórios organizados
        self.categories_dir = SETTINGS.categories_dir
        self.restaurants_dir = SETTINGS.restaurants_dir
        self.products_dir = SETTINGS.products_dir
        self.metadata_dir = SETTINGS.output_dir
        
        self.ensure_database_dirs()
        
        # Arquivos principais
        self.categories_file = f"{self.categories_dir}/{db_name}_categories.csv"
        self.metadata_file = f"{self.metadata_dir}/{db_name}_metadata.json"
        
        # Cache de IDs para verificação rápida
        self.category_ids: Set[str] = set()
        self.restaurant_ids: Set[str] = set()
        self.product_ids: Set[str] = set()
        
        # Carrega IDs existentes
        self._load_existing_ids()
    
    def ensure_database_dirs(self):
        """Garante que todos os diretórios do banco existem"""
        os.makedirs(self.categories_dir, exist_ok=True)
        os.makedirs(self.restaurants_dir, exist_ok=True)
        os.makedirs(self.products_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def _generate_id(self, data: Dict[str, Any], fields: List[str]) -> str:
        """Gera ID único baseado em campos específicos"""
        id_string = ""
        for field in fields:
            value = data.get(field, "")
            id_string += str(value).lower().strip()
        
        return hashlib.md5(id_string.encode()).hexdigest()
    
    def _load_existing_ids(self):
        """Carrega IDs existentes dos arquivos CSV"""
        # Carrega IDs de categorias
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row:
                        self.category_ids.add(row['id'])
            self.logger.info(f"Carregadas {len(self.category_ids)} categorias existentes")
        
        # Carrega IDs de restaurantes de todos os arquivos
        restaurant_files = list(Path(self.restaurants_dir).glob(f"{self.db_name}_restaurantes_*.csv"))
        total_restaurants = 0
        for file_path in restaurant_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row:
                        self.restaurant_ids.add(row['id'])
                        total_restaurants += 1
        if total_restaurants > 0:
            self.logger.info(f"Carregados {len(self.restaurant_ids)} IDs únicos de restaurantes")
        
        # Carrega IDs de produtos de todos os arquivos
        product_files = list(Path(self.products_dir).glob(f"{self.db_name}_produtos_*.csv"))
        total_products = 0
        for file_path in product_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row:
                        self.product_ids.add(row['id'])
                        total_products += 1
        if total_products > 0:
            self.logger.info(f"Carregados {len(self.product_ids)} IDs únicos de produtos")
    
    def save_categories(self, categories: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
        """Salva categorias no banco de dados, evitando duplicatas"""
        new_categories = []
        duplicates = 0
        
        for cat in categories:
            # Gera ID único baseado no nome e cidade
            cat_data = cat if isinstance(cat, dict) else cat.to_dict()
            cat_data['city'] = city
            cat_data['id'] = self._generate_id(cat_data, ['name', 'city'])
            
            # Verifica se já existe
            if cat_data['id'] in self.category_ids:
                duplicates += 1
                self.logger.debug(f"Categoria duplicada ignorada: {cat_data['name']}")
                continue
            
            # Adiciona timestamp se não existir
            if 'extracted_at' not in cat_data:
                cat_data['extracted_at'] = datetime.now().isoformat()
            
            new_categories.append(cat_data)
            self.category_ids.add(cat_data['id'])
        
        # Salva apenas novas categorias
        if new_categories:
            file_exists = os.path.exists(self.categories_file)
            
            with open(self.categories_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'name', 'url', 'slug', 'city', 'icon_url', 'extracted_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Escreve header apenas se arquivo não existe
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(new_categories)
            
            self.logger.info(f"SUCESSO: {len(new_categories)} novas categorias salvas")
        
        # Atualiza metadata
        self._update_metadata('categories', len(new_categories), duplicates)
        
        return {
            'new': len(new_categories),
            'duplicates': duplicates,
            'total': len(self.category_ids)
        }
    
    def save_restaurants(self, restaurants: List[Dict[str, Any]], category: str, city: str) -> Dict[str, Any]:
        """Salva restaurantes no banco de dados em arquivo específico da categoria"""
        new_restaurants = []
        duplicates = 0
        
        # Cria arquivo específico para a categoria na pasta restaurants
        category_safe = category.lower().replace(' ', '_').replace('&', 'e').replace('ã', 'a').replace('ç', 'c')
        category_file = f"{self.restaurants_dir}/{self.db_name}_restaurantes_{category_safe}.csv"
        
        # Carrega IDs existentes para esta categoria específica
        category_ids = set()
        if os.path.exists(category_file):
            with open(category_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row:
                        category_ids.add(row['id'])
        
        for rest in restaurants:
            # Gera ID único baseado no nome, categoria e cidade
            rest_data = rest if isinstance(rest, dict) else rest.to_dict()
            rest_data['category'] = category
            rest_data['city'] = city
            rest_data['id'] = self._generate_id(rest_data, ['nome', 'category', 'city'])
            
            # Verifica se já existe nesta categoria específica
            if rest_data['id'] in category_ids:
                duplicates += 1
                self.logger.debug(f"Restaurante duplicado ignorado: {rest_data.get('nome', 'Unknown')}")
                continue
            
            # Adiciona timestamp se não existir
            if 'extracted_at' not in rest_data:
                rest_data['extracted_at'] = datetime.now().isoformat()
            
            new_restaurants.append(rest_data)
            category_ids.add(rest_data['id'])
            self.restaurant_ids.add(rest_data['id'])  # Mantém cache global também
        
        # Salva apenas novos restaurantes no arquivo da categoria
        if new_restaurants:
            file_exists = os.path.exists(category_file)
            
            with open(category_file, 'a', newline='', encoding='utf-8') as f:
                # Define campos baseado no primeiro restaurante
                if new_restaurants:
                    fieldnames = ['id'] + [k for k in new_restaurants[0].keys() if k != 'id']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Escreve header apenas se arquivo não existe
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerows(new_restaurants)
            
            self.logger.info(f"SUCESSO: {len(new_restaurants)} novos restaurantes salvos em {category_file}")
        
        # Atualiza metadata
        self._update_metadata('restaurants', len(new_restaurants), duplicates)
        
        return {
            'new': len(new_restaurants),
            'duplicates': duplicates,
            'total': len(category_ids),
            'file': category_file
        }
    
    def _update_metadata(self, data_type: str, new_count: int, duplicate_count: int):
        """Atualiza arquivo de metadata com estatísticas"""
        metadata = {}
        
        # Carrega metadata existente
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Inicializa estrutura se não existe
        if 'statistics' not in metadata:
            metadata['statistics'] = {}
        
        if data_type not in metadata['statistics']:
            metadata['statistics'][data_type] = {
                'total_saved': 0,
                'total_duplicates': 0,
                'last_update': None
            }
        
        # Atualiza estatísticas
        metadata['statistics'][data_type]['total_saved'] += new_count
        metadata['statistics'][data_type]['total_duplicates'] += duplicate_count
        metadata['statistics'][data_type]['last_update'] = datetime.now().isoformat()
        metadata['database_name'] = self.db_name
        metadata['created_at'] = metadata.get('created_at', datetime.now().isoformat())
        
        # Salva metadata
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        stats = {
            'categories': {
                'total': len(self.category_ids),
                'file': self.categories_file
            },
            'restaurants': {
                'total': len(self.restaurant_ids),
                'file': self.restaurants_file
            }
        }
        
        # Adiciona metadata se existir
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                stats['metadata'] = metadata
        
        return stats
    
    def get_existing_categories(self, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna categorias existentes no banco"""
        categories = []
        
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if city is None or row.get('city') == city:
                        categories.append(row)
        
        return categories
    
    def category_exists(self, name: str, city: str) -> bool:
        """Verifica se uma categoria já existe"""
        cat_id = self._generate_id({'name': name, 'city': city}, ['name', 'city'])
        return cat_id in self.category_ids
    
    def restaurant_exists(self, name: str, category: str, city: str) -> bool:
        """Verifica se um restaurante já existe"""
        rest_id = self._generate_id(
            {'nome': name, 'category': category, 'city': city}, 
            ['nome', 'category', 'city']
        )
        return rest_id in self.restaurant_ids
    
    def save_products(self, products: List[Dict[str, Any]], restaurant_name: str, restaurant_id: str) -> Dict[str, Any]:
        """Salva produtos no banco de dados, evitando duplicatas"""
        new_products = []
        duplicates = 0
        
        # Arquivo específico por restaurante na pasta products
        restaurant_safe = restaurant_name.lower().replace(' ', '_').replace('&', 'e')
        restaurant_safe = ''.join(c for c in restaurant_safe if c.isalnum() or c == '_')[:50]
        products_file = f"{self.products_dir}/{self.db_name}_produtos_{restaurant_safe}.csv"
        
        # Carrega IDs existentes para este restaurante
        existing_product_ids = set()
        if os.path.exists(products_file):
            with open(products_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row:
                        existing_product_ids.add(row['id'])
        
        for product in products:
            # Gera ID único baseado no nome do produto e restaurante
            product_data = product if isinstance(product, dict) else product.to_dict()
            product_data['restaurant_id'] = restaurant_id
            product_data['restaurant_name'] = restaurant_name
            product_data['id'] = self._generate_id(
                product_data, 
                ['nome', 'restaurant_id']
            )
            
            # Verifica se já existe
            if product_data['id'] in existing_product_ids or product_data['id'] in self.product_ids:
                duplicates += 1
                self.logger.debug(f"Produto duplicado ignorado: {product_data.get('nome', 'Unknown')}")
                continue
            
            # Adiciona timestamp se não existir
            if 'extracted_at' not in product_data:
                product_data['extracted_at'] = datetime.now().isoformat()
            
            new_products.append(product_data)
            self.product_ids.add(product_data['id'])
        
        # Salva apenas novos produtos
        if new_products:
            file_exists = os.path.exists(products_file)
            
            with open(products_file, 'a', newline='', encoding='utf-8') as f:
                # Define campos baseado no primeiro produto
                if new_products:
                    fieldnames = ['id'] + [k for k in new_products[0].keys() if k != 'id']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Escreve header apenas se arquivo não existe
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerows(new_products)
            
            self.logger.info(f"SUCESSO: {len(new_products)} novos produtos salvos em {products_file}")
        
        # Atualiza metadata
        self._update_metadata('products', len(new_products), duplicates)
        
        return {
            'new': len(new_products),
            'duplicates': duplicates,
            'total': len(existing_product_ids) + len(new_products),
            'file': products_file
        }
    
    def get_restaurants_with_urls(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna restaurantes que possuem URL para extração de produtos"""
        restaurants_with_urls = []
        
        # Busca em todos os arquivos de restaurantes
        restaurant_files = list(Path(self.restaurants_dir).glob(f"{self.db_name}_restaurantes_*.csv"))
        
        for file_path in restaurant_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Verifica se tem URL válida
                    url = row.get('url', '').strip()
                    if url and url != 'None' and url.startswith('http'):
                        restaurants_with_urls.append({
                            'id': row.get('id'),
                            'nome': row.get('nome'),
                            'categoria': row.get('categoria'),
                            'url': url,
                            'avaliacao': row.get('avaliacao', 0),
                            'cidade': row.get('city', row.get('cidade'))
                        })
                        
                        if limit and len(restaurants_with_urls) >= limit:
                            return restaurants_with_urls
        
        return restaurants_with_urls