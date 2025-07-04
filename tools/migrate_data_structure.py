#!/usr/bin/env python3
"""
Ferramenta para migrar dados existentes para a nova estrutura organizada
"""

import os
import shutil
from pathlib import Path


def migrate_data_structure():
    """Migra dados para nova estrutura de pastas"""
    print("🔄 Migrando estrutura de dados...")
    
    data_dir = Path("data")
    
    # Contadores
    moved_categories = 0
    moved_restaurants = 0
    moved_products = 0
    
    if not data_dir.exists():
        print("❌ Diretório 'data' não encontrado")
        return
    
    # Cria estrutura de pastas
    categories_dir = data_dir / "categories"
    restaurants_dir = data_dir / "restaurants"
    products_dir = data_dir / "products"
    
    categories_dir.mkdir(exist_ok=True)
    restaurants_dir.mkdir(exist_ok=True)
    products_dir.mkdir(exist_ok=True)
    
    print(f"📁 Estrutura de pastas criada:")
    print(f"   {categories_dir}")
    print(f"   {restaurants_dir}")
    print(f"   {products_dir}")
    
    # Migra arquivos existentes
    for file_path in data_dir.glob("*.csv"):
        filename = file_path.name
        
        # Categorias
        if "_categories.csv" in filename:
            destination = categories_dir / filename
            if not destination.exists():
                shutil.move(str(file_path), str(destination))
                moved_categories += 1
                print(f"✅ Categoria: {filename} → categories/")
        
        # Restaurantes
        elif "_restaurantes_" in filename:
            destination = restaurants_dir / filename
            if not destination.exists():
                shutil.move(str(file_path), str(destination))
                moved_restaurants += 1
                print(f"✅ Restaurantes: {filename} → restaurants/")
        
        # Produtos
        elif "_produtos_" in filename:
            destination = products_dir / filename
            if not destination.exists():
                shutil.move(str(file_path), str(destination))
                moved_products += 1
                print(f"✅ Produtos: {filename} → products/")
    
    # Relatório final
    print(f"\n📊 Migração concluída:")
    print(f"   Categorias movidas: {moved_categories}")
    print(f"   Restaurantes movidos: {moved_restaurants}")
    print(f"   Produtos movidos: {moved_products}")
    
    # Mostra estrutura final
    print(f"\n📂 Estrutura final:")
    print(f"data/")
    print(f"├── categories/")
    for f in sorted(categories_dir.glob("*.csv")):
        print(f"│   └── {f.name}")
    print(f"├── restaurants/")
    for f in sorted(restaurants_dir.glob("*.csv")):
        print(f"│   └── {f.name}")
    print(f"├── products/")
    for f in sorted(products_dir.glob("*.csv")):
        print(f"│   └── {f.name}")
    print(f"└── ifood_data_metadata.json")
    
    print(f"\n✨ Migração concluída com sucesso!")


if __name__ == "__main__":
    try:
        migrate_data_structure()
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()